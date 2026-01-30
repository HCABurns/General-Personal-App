package com.example.arsenal_app.database;

import android.content.Context;
import android.content.SharedPreferences;

import androidx.preference.PreferenceManager;

import com.example.arsenal_app.R;

public class SettingsManager {

    private SharedPreferences prefs;
    private SharedPreferences.OnSharedPreferenceChangeListener listener;
    private Context context;

    public SettingsManager() {
        // Empty constructor
    }

    public void setPrefs(Context context) {
        this.context = context.getApplicationContext(); // ✅ Save application context

        prefs = PreferenceManager.getDefaultSharedPreferences(this.context);

        listener = (prefs, key) -> {
            System.out.println("Preference changed: " + key);

            if ("default_team".equals(key)) {
                String newTeam = prefs.getString("default_team", getDefaultTeam());
                if (newTeam != null) {
                    System.out.println("Team changed to: " + newTeam);
                    // Code here
                }
            }
        };

        prefs.registerOnSharedPreferenceChangeListener(listener);
    }

    public String getTeam() {
        String team = prefs.getString("default_team", getDefaultTeam());
        System.out.println("Default team value: " + team);
        return team.toLowerCase();
    }

    private String getDefaultTeam() {
        return context.getString(R.string.default_team);
    }

    public void cleanup() {
        if (prefs != null && listener != null) {
            prefs.unregisterOnSharedPreferenceChangeListener(listener);
        }
    }
}
