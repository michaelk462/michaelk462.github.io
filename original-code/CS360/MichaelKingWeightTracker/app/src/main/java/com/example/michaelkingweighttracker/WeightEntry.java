/*****CODE INFORMATION*****
 * Name: Michael King
 * Date: 2/22/2026
 * File: WeightEntry.java
 * Assignment: Project Three
 * Application Name: "WeightTracker"
 * Option 3 - Weight Tracking App
 * University: SNHU
 */

//***Package for WeightTracker***
package com.example.michaelkingweighttracker;

//***Weight Entry Class***
public class WeightEntry {

    //***Declare Variables (id, date and weight)***
    private final long id; //weight ID
    private final String date;//weight Date
    private final double weight;//weight

    //***Constructor for Variables***
    public WeightEntry(long id, String date, double weight) {
        this.id = id;
        this.date = date;
        this.weight = weight;
    }//end constructor

    //Getters
    public long getId() {return id;}
    public String getDate() {return date;}
    public double getWeight() {return weight;}

}
