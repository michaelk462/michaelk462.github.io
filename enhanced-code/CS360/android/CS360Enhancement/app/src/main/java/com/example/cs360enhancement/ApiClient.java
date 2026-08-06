/*****CODE INFORMATION*****
 * Name: Michael King
 * File: ApiClient.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Purpose ---
 * Builds the Retrofit/OkHttp client used to talk to the Flask API,
 * and attaches the stored JWT to every outgoing request.
 */

package com.example.cs360enhancement;

import android.content.Context;

import androidx.annotation.NonNull;

import java.util.concurrent.TimeUnit;
import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import java.io.IOException;
public class ApiClient {

    // 10.0.2.2 is how the Android emulator reaches the host machine's
    // localhost. Point this at your deployed server's HTTPS URL for a
    // physical device or production use.
    private static final String BASE_URL = "http://10.0.2.2:5000/";

    private static Retrofit retrofit;

    public static WeightApiService getService(Context context) {
        if (retrofit == null) {
            TokenManager tokenManager = new TokenManager(context.getApplicationContext());

            Interceptor authInterceptor = new Interceptor() {
                @NonNull
                @Override
                public Response intercept(Chain chain) throws IOException {
                    Request original = chain.request();
                    String token = tokenManager.getToken();
                    if (token == null) {
                        return chain.proceed(original);
                    }
                    Request authed = original.newBuilder()
                            .header("Authorization", "Bearer " + token)
                            .build();
                    return chain.proceed(authed);
                }
            };

            HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
            // BODY level is convenient for debugging but would leak
            // credentials/tokens into logcat
            // Keep this at BASIC or NONE outside local development.
            logging.setLevel(HttpLoggingInterceptor.Level.BASIC);

            OkHttpClient httpClient = new OkHttpClient.Builder()
                    .addInterceptor(authInterceptor)
                    .addInterceptor(logging)
                    .connectTimeout(15, TimeUnit.SECONDS)
                    .readTimeout(15, TimeUnit.SECONDS)
                    .build();

            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .client(httpClient)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit.create(WeightApiService.class);
    }
}
