/*****CODE INFORMATION*****
 * Name: Michael King
 * File: WeightApiService.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Purpose ---
 * Retrofit interface describing the Flask REST API. Replaces
 * direct SQLite access (formerly WeightDAO.java) with HTTP calls
 * against a MongoDB-backed server.
 */

// *** Package for Weight Tracker Enhancement ***
package com.example.cs360enhancement;

// *** Java, Android and Retrofit Imports ***
import com.example.cs360enhancement.models.AuthRequest;
import com.example.cs360enhancement.models.AuthResponse;
import com.example.cs360enhancement.models.GoalDto;
import com.example.cs360enhancement.models.WeightEntryDto;
import java.util.List;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.PUT;
import retrofit2.http.POST;
import retrofit2.http.Path;

public interface WeightApiService {

    @POST("api/register")
    Call<AuthResponse> register(@Body AuthRequest request);

    @POST("api/login")
    Call<AuthResponse> login(@Body AuthRequest request);

    @GET("api/entries")
    Call<List<WeightEntryDto>> getEntries();

    @POST("api/entries")
    Call<WeightEntryDto> addEntry(@Body WeightEntryDto entry);

    @PUT("api/entries/{id}")
    Call<WeightEntryDto> updateEntry(@Path("id") String id, @Body WeightEntryDto entry);

    @DELETE("api/entries/{id}")
    Call<Void> deleteEntry(@Path("id") String id);

    @GET("api/goal")
    Call<GoalDto> getGoal();

    @PUT("api/goal")
    Call<GoalDto> setGoal(@Body GoalDto goal);
}
