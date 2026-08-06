/*****CODE INFORMATION*****
 * Name: Michael King
 * File: WeightEntryDto.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Purpose ---
 * Represents a weight entry as sent to/from the REST API.
 * Replaces the SQLite-backed WeightEntry.java as the model used
 * by network calls. The id is a MongoDB ObjectId string rather than
 * a SQLite long row id.
 */

package com.example.cs360enhancement.models;
import com.google.gson.annotations.SerializedName;

public class WeightEntryDto {

    @SerializedName("id")
    private String id;

    @SerializedName("date")
    private String date;

    @SerializedName("weight")
    private double weight;

    // Used when building an outgoing request (id is assigned server-side).
    public WeightEntryDto(String date, double weight) {
        this.date = date;
        this.weight = weight;
    }

    public String getId() { return id; }
    public String getDate() { return date; }
    public double getWeight() { return weight; }
}
