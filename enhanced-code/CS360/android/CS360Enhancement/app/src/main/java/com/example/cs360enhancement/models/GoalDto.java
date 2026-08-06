/*****CODE INFORMATION*****
 * Name: Michael King
 * File: GoalDto.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Purpose ---
 * Request/Response body for /api/goal (GET and PUT)
 */

package com.example.cs360enhancement.models;
import com.google.gson.annotations.SerializedName;

public class GoalDto {
    @SerializedName("goalWeight")
    private Double goalWeight; //Double (not double) so "no goal set"; null works

    public GoalDto(double goalWeight) {
        this.goalWeight = goalWeight;
    }

    public double getGoalWeight() {
        return goalWeight == null ? -1 : goalWeight;
    }
}
