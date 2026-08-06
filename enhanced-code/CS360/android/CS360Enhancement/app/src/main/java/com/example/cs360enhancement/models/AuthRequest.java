/*****CODE INFORMATION*****
 * Name: Michael King
 * File: AuthRequest.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Purpose ---
 * Request body for /api/login and /api/register
 */

package com.example.cs360enhancement.models;

public class AuthRequest {

    private final String username;
    private final String password;

    public AuthRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public String getUsername() {return username;}
    public String getPassword() {return password;}
}
