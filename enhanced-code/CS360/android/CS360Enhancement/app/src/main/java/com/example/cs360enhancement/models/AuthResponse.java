/*****CODE INFORMATION*****
 * Name: Michael King
 * File: AuthResponse.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Purpose ---
 * Response body from /api/login (JWT token) and /api/register
 * (message), and generic error messages from the API.
 */

package com.example.cs360enhancement.models;
import com.google.gson.annotations.SerializedName;

public class AuthResponse {

    @SerializedName("token")
    private String token;

    @SerializedName("message")
    private String message;

    @SerializedName("error")
    private String error;

    public String getToken() {return token;}
    public String getMessage() {return message;}
    public String getError() {return error;}
}
