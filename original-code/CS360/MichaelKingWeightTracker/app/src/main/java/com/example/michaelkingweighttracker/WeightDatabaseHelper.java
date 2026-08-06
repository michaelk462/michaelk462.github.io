/*****CODE INFORMATION*****
 * Name: Michael King
 * Date: 2/22/2026
 * File: WeightDatabaseHelper.java
 * Assignment: Project Three
 * Application Name: "WeightTracker"
 * Option 3 - Weight Tracking App
 * University: SNHU
 */

//***Package for Weight Tracker***
package com.example.michaelkingweighttracker;

//***Java/Android Imports***
import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class WeightDatabaseHelper extends SQLiteOpenHelper {

    //Declare All Variables for Database Tables
    public static final String dbName = "weight_tracker.db"; //database name
    public static final int dbVersion = 1; //database version
    public static final String tbWeight = "weight_entries"; //table weight entries
    public static final String columnID = "_id"; //column ID
    public static final String columnDate = "date"; //column date
    public static final String columnWeight = "weight"; //column weight
    public static final String tbUsers = "users"; //table users
    public static final String columnUsername = "username"; //column username
    public static final String columnPassword = "password"; //column password
    public static final String columnGoalWeight = "goal_weight"; //goal weight
    public static final String columnPhone = "phone_number"; //phone number

    //Create Table for Weight Entries
    private static final String createWeightTable =
            "Create Table " + tbWeight + " (" +
                    columnID + " Integer Primary Key Autoincrement, " +
                    columnDate + " Text Not Null, " +
                    columnWeight + " Real Not Null);";

    //Create Table for Users
    private static final String createUsersTable =
            "Create Table " + tbUsers + " (" +
                    columnID + " Integer Primary Key Autoincrement, " +
                    columnUsername + " Text Unique Not Null, " +
                    columnPassword + " Text  Not Null, " +
                    columnGoalWeight + " Real, " +
                    columnPhone + " Text);";

    //Use WeightDatabaseHelper for This Class
    public WeightDatabaseHelper(Context context) {
        super (context, dbName, null, dbVersion);
    }

    //Create Weight Entry and Users Tables For Database
    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(createWeightTable); //weight entry table
        db.execSQL(createUsersTable);  //users table
    }//end method

    //Upgrade Weight Entry and Users Tables from old to new Versions
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL(createWeightTable); //weight entry table
        db.execSQL(createUsersTable);  //users table
    }//end method
}//end class