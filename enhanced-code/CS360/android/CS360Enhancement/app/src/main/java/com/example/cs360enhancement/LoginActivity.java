/*****CODE INFORMATION*****
 * Name: Michael King
 * File: LoginActivity.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Enhancement Notes ---
 * Login/Registration now go through the Flask/MongoDB REST API
 * (WeightApiService) instead of the local SQLite WeightDAO.
 * On a successful login, the JWT returned by the server is stored
 * vis TokenManager and reused on every subsequent request.
 */

// ***Package for Login Activity***
package com.example.cs360enhancement;

// ***Java/Android Imports***
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.example.cs360enhancement.models.AuthRequest;
import com.example.cs360enhancement.models.AuthResponse;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

//***Main Activity Class***
public class LoginActivity extends AppCompatActivity {

    //Declare Variables for Username, Password, and Weight Database
    private EditText textUsername, textPassword;
    private WeightApiService apiService;
    private TokenManager tokenManager;

    //***Method to Create User Account by Implementing Elements***
    @Override
    protected void onCreate (Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        //Initialize API service and token storage
        apiService = ApiClient.getService(this);
        tokenManager = new TokenManager(this);

        //Declare UI Elements
        textUsername = findViewById(R.id.textUsername);
        textPassword = findViewById(R.id.textPassword);
        Button loginButton = findViewById(R.id.loginButton);
        Button registerButton = findViewById(R.id.registerButton);

        //Clear Text From EditTexts
        textUsername.setText("");
        textPassword.setText("");

        //Set Up Click Listener for Login/Register Buttons
        loginButton.setOnClickListener(v -> handleLogin());
        registerButton.setOnClickListener(v -> registerUser());
    }//end method

    //***Method to Verify User Credentials (Login)***
    private void handleLogin() {
        //Declare Username and Password
        String username = textUsername.getText().toString().trim();
        String password = textPassword.getText().toString().trim();

        //Validate Username and Password Input
        if (username.isEmpty()) {
            //Displays error message if username is not entered
            textUsername.setError("ERROR: Username empty. Please enter Username.");

            return;
        }//end if

        if (password.isEmpty()) {
            //Displays error message if password is not entered
            textUsername.setError("ERROR: Password empty. Please enter Password.");
            textUsername.requestFocus();
            return;
        }//end if

        apiService.login(new AuthRequest(username, password)).enqueue(new Callback<>() {
            @Override
            public void onResponse(@NonNull Call<AuthResponse> call, @NonNull Response<AuthResponse> response) {
                if (response.isSuccessful() && response.body() != null
                        && response.body().getToken() != null) {
                    tokenManager.saveSession(response.body().getToken(), username);

                    //Navigate to the Weight Display Activity
                    Intent intent = new Intent(LoginActivity.this, WeightDisplayActivity.class);
                    intent.putExtra("username", username);
                    startActivity(intent);
                    finish(); //Finishes Login Activity
                } else {
                    // 401 or malformed response = invalid credentials
                    Toast.makeText(LoginActivity.this,
                            "ERROR: Invalid username/password", Toast.LENGTH_LONG).show();
                }//end if
            }//end onResponse

            @Override
            public void onFailure(@NonNull Call<AuthResponse> call, @NonNull Throwable t) {
                Toast.makeText(LoginActivity.this,
                        "Could not reach server: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }//end onFailure
        });
    }//end method

    //***Method to Create New User Credentials (Register)***
    private void registerUser() {
        //Declare Username and Password
        String username = textUsername.getText().toString().trim();
        String password = textPassword.getText().toString().trim();

        //Validate Username and Password Input
        if (username.isEmpty()) {
            //Displays error message if username is not entered
            textUsername.setError("ERROR: Username empty. Please enter Username.");
            textUsername.requestFocus();
            return;
        }//end if

        if (password.isEmpty()) {
            //Displays error message if password is not entered
            textUsername.setError("ERROR: Password empty. Please enter Password.");
            textUsername.requestFocus();
            return;
        }//end if

        apiService.register(new AuthRequest(username, password)).enqueue(new Callback<>() {
            @Override
            public void onResponse(@NonNull Call<AuthResponse> call, @NonNull Response<AuthResponse> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(LoginActivity.this,
                            "Account Created, Please Login.", Toast.LENGTH_LONG).show();
                } else if (response.code() == 409) {
                    Toast.makeText(LoginActivity.this,
                            "Username Already Exists.", Toast.LENGTH_LONG).show();
                } else {
                    Toast.makeText(LoginActivity.this,
                            "Registration Failed. Check Username/Password Requirements", Toast.LENGTH_LONG).show();
                } //end if
            }//end onResponse

            @Override
            public void onFailure(@NonNull Call<AuthResponse> call, @NonNull Throwable t) {
                Toast.makeText(LoginActivity.this,
                        "Could not reach server: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }//end onFailure
        });
    }//end method
}//end class
