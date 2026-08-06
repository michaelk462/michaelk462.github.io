/*****CODE INFORMATION*****
 * Name: Michael King
 * File: TokenManager.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Purpose ---
 * Stores the JWT issued by the API in EncryptedSharedPreferences
 * rather than plain SharedPreferences, so the token is unreadable
 * if the device's shared-prefs file is extracted
 * --- Requires ---
 * androidx.security:security-crypto in build.gradle
 */

package com.example.cs360enhancement;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import androidx.security.crypto.EncryptedSharedPreferences;
import androidx.security.crypto.MasterKey;
import java.io.IOException;
import java.security.GeneralSecurityException;

public class TokenManager {

    private static final String TAG = "TokenManager";
    private static final String PREFS_NAME = "secure_auth_prefs";
    private static final String KEY_TOKEN = "jwt_token";
    private static final String KEY_USERNAME = "current_username";

    private final SharedPreferences prefs;

    public TokenManager(Context context) {
        SharedPreferences created;
        try{
            MasterKey masterKey = new MasterKey.Builder(context)
                    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                    .build();
            created = EncryptedSharedPreferences.create(
                    context,
                    PREFS_NAME,
                    masterKey,
                    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            );
        } catch (GeneralSecurityException | IOException e ) {
            // Falls back to regular prefs only if encryption setup itself fails
            // (e.g. unsupported device keystore)
            // logged for diagnosis, never silently swallowed.
            Log.e(TAG, "Failed to create encrypted prefs, falling back.", e);
            created = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        }
        this.prefs = created;
    }

    public void saveSession(String token, String username) {
        prefs.edit()
                .putString(KEY_TOKEN, token)
                .putString(KEY_USERNAME, username)
                .apply();
    }

    public String getToken() {
        return prefs.getString(KEY_TOKEN, null);
    }

    public String getUsername() {
        return prefs.getString(KEY_USERNAME, null);
    }

    public boolean isLoggedIn() {
        return getToken() != null;
    }

    public void clearSession() {
        prefs.edit().clear().apply();
    }
}
