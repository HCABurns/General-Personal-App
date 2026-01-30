package com.example.arsenal_app.database;

import com.example.arsenal_app.Activities.MainActivity;
import com.example.arsenal_app.models.Game;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;


/**
 * Singleton class responsible for coordinating data access and storage.
 * Acts as a central repository for caching and retrieving data,
 * ensuring API calls aren't duplicated unnecessarily.
 */
public class DataRepository {

    // Singleton instance.
    public static DataRepository instance;

    // Database helper for local data caching.
    private final DBHelper dbHelper;

    // API helper for remote data fetching.
    private final API api;

    // Tracks if a given endpoint is currently being fetched to prevent duplicate calls.
    Map<String, Boolean> isFetchingMap = new HashMap<>();

    // Stores waiting callbacks for endpoints that are already being fetched.
    Map<String, List<DataStatus<?>>> waitingCallbacksMap = new HashMap<>();

    // Get preferences:
    private final SettingsManager settingsManager;

    /**
     * Private constructor to create dbHelper and API.
     */
    private DataRepository() {
        dbHelper = new DBHelper();
        api = new API();
        settingsManager = new SettingsManager();
    }

    /**
     * Returns the singleton instance of DataRepository.
     * @return singleton instance
     */
    public static synchronized DataRepository getInstance() {
        if (instance == null) {
            instance = new DataRepository();
        }
        return instance;
    }

    public DBHelper getDbHelper() {
        return dbHelper;
    }

    public API getApi() {
        return api;
    }

    public SettingsManager getSettingsManager(){return settingsManager;}

    /**
     * Loads EpicGames data, either from local cache or by making an API call.
     * @param url The url of the API endpoint to call
     * @param jsonArrayKey The JSON array key in the response
     * @param clazz The class type for deserialization
     * @param callback The callback to notify when data is loaded
     * @param functionSetter A setter to process or store the data
     * @param <T> Generic type of data
     */
    public <T> void loadAllEpicGames(String url, String jsonArrayKey, Class<T> clazz,
                                     DataStatus<T> callback, Consumer<ArrayList<T>> functionSetter) {
        if (dbHelper.getEpicGames() != null && !dbHelper.getEpicGames().isEmpty()) {
            callback.onDataLoaded((ArrayList<T>) dbHelper.getEpicGames());
        } else {
            api.fetchData(url, jsonArrayKey, clazz, callback, functionSetter);
        }
    }

    /**
     * Loads FootballGames data, coordinating API calls to avoid duplicates
     * and queueing callbacks for concurrent requests.
     * @param url The url of the API endpoint to call
     * @param jsonArrayKey The JSON array key in the response
     * @param clazz The class type for deserialization
     * @param callback The callback to notify when data is loaded
     * @param functionSetter A setter to process or store the data
     * @param <T> Generic type of data
     */
    public <T> void loadAllFootballGames(String url, String jsonArrayKey, Class<T> clazz,
                                         DataStatus<T> callback, Consumer<ArrayList<T>> functionSetter) {
        ArrayList<Game> cached = dbHelper.getGames();
        // If data is cached, return it immediately
        if (cached != null && !cached.isEmpty()) {
            callback.onDataLoaded((ArrayList<T>) cached);
            return;
        }

        // If already fetching this data, queue the callback
        if (Boolean.TRUE.equals(isFetchingMap.get(url))) {
            List<DataStatus<?>> waitingList = waitingCallbacksMap.get(url);
            if (waitingList == null) {
                waitingList = new ArrayList<>();
                waitingCallbacksMap.put(url, waitingList);
            }
            waitingList.add(callback);
            return;
        }

        // Mark as fetching to stop duplicate calls and initialize waiting list.
        isFetchingMap.put(url, true);
        List<DataStatus<?>> waitingList = new ArrayList<>();
        waitingList.add(callback);
        waitingCallbacksMap.put(url, waitingList);

        api.fetchData(url, jsonArrayKey, clazz, new DataStatus<T>() {
            @Override
            public void onDataLoaded(ArrayList<T> dataList) {
                // Remove any games with time before it
                ArrayList<Game> newDataList = new ArrayList<>();
                long milliseconds = 0;
                System.out.println("HERE 1");
                for (Game game : (ArrayList<Game>) dataList){
                    System.out.println("HERE");
                    String[] dateParts = game.getDate().split("-");
                    int year = Integer.parseInt(dateParts[0]);
                    int month = Integer.parseInt(dateParts[1]);
                    int day = Integer.parseInt(dateParts[2]);

                    String[] timeParts = game.getTime().split(":");
                    int hours = Integer.parseInt(timeParts[0]);
                    int minutes = Integer.parseInt(timeParts[1]);
                    int seconds;
                    if (timeParts.length > 2) {
                        seconds = Integer.parseInt(timeParts[2]);
                    } else {
                        seconds = 0;
                    }
                    LocalDateTime pastDateTime;
                    LocalDateTime now;
                    milliseconds = -1;
                    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                        pastDateTime = LocalDateTime.of(year, month, day, hours, minutes, seconds);
                        now = LocalDateTime.now();
                        milliseconds = Duration.between(now, pastDateTime).getSeconds() * 1000;
                    }
                    System.out.println(game + " : " + milliseconds);
                    if (milliseconds > 0){
                        newDataList.add(game);
                        System.out.println("Game added");
                    }
                }
                dataList = (ArrayList<T>) newDataList;
                // Cache the data
                dbHelper.setGames(newDataList);

                // Let the caller process the data
                functionSetter.accept(dataList);

                // Notify all waiting callbacks of data loaded.
                List<DataStatus<?>> callbacks = waitingCallbacksMap.get(url);
                if (callbacks != null) {
                    for (DataStatus<?> ds : callbacks) {
                        ((DataStatus<T>) ds).onDataLoaded(dataList);
                    }
                }

                // Clean up
                waitingCallbacksMap.remove(url);
                isFetchingMap.remove(url);
            }

            @Override
            public void onError(String errorMessage) {
                // Notify all waiting callbacks about the error
                List<DataStatus<?>> callbacks = waitingCallbacksMap.get(url);
                if (callbacks != null) {
                    for (DataStatus<?> ds : callbacks) {
                        ds.onError(errorMessage);
                    }
                }
                // Clean up
                waitingCallbacksMap.remove(url);
                isFetchingMap.remove(url);
            }
        }, functionSetter);
    }

    /**
     * Loads Races data either from local cache or from API.
     * @param url The url of the API endpoint to call
     * @param jsonArrayKey The JSON array key in the response
     * @param clazz The class type for deserialization
     * @param callback The callback to notify when data is loaded
     * @param functionSetter A setter to process or store the data
     * @param <T> Generic type of data
     */
    public <T> void loadAllRaces(String url, String jsonArrayKey, Class<T> clazz,
                                 DataStatus<T> callback, Consumer<ArrayList<T>> functionSetter) {
        if (dbHelper.getRaces() != null && !dbHelper.getRaces().isEmpty()) {
            callback.onDataLoaded((ArrayList<T>) dbHelper.getRaces());
        } else {
            api.fetchData(url, jsonArrayKey, clazz, callback, functionSetter);
        }
    }
}
