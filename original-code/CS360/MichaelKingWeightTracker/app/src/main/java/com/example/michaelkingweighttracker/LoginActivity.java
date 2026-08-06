/*****CODE INFORMATION*****
 * Name: Michael King
 * Date: 2/22/2026
 * File: LoginActivity.java
 * Assignment: Project Three
 * Application Name: "WeightTracker"
 * Option 3 - Weight Tracking App
 * University: SNHU
 */

// ***Package for Login Activity***
package com.example.michaelkingweighttracker;

// ***Java/Android Imports***
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

//***Main Activity Class***
public class LoginActivity extends AppCompatActivity {

    //Declare Variables for Username, Password, and Weight Database
    private EditText textUsername, textPassword;
    private WeightDAO weightDAO;

    //***Method to Create User Account by Implementing Elements***
    @Override
    protected void onCreate (Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        //Initialize Weight Database
        weightDAO = new WeightDAO(this);

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

        if (weightDAO.validateUser(username, password)) {
            //Navigate to the Database Activity
            Intent intent = new Intent(this, WeightDisplayActivity.class);
            intent.putExtra("Username", username);
            startActivity(intent);
            finish(); //Finishes Login Activity
        } else {
            //Displays error message if username and/or password are incorrect
            Toast.makeText(this, "ERROR: Invalid username/password", Toast.LENGTH_LONG).show();
        }//end if
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

        long result = weightDAO.addUser(username, password);
        if (result != -1) {
            //Displays message if user account is created and asks user to log in
            //with same credentials used to create the account
            Toast.makeText(this, "Account Created, Please login.", Toast.LENGTH_LONG).show();
        } else { //Displays message if user attempts to create account with same username
            Toast.makeText(this, "Username Already Exists.", Toast.LENGTH_LONG).show();
        }//end if
    }//end method
}//end class
