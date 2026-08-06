/*****CODE INFORMATION*****
 * Name: Michael King
 * Date: 2/22/2026
 * File: WeightDAO.java
 * Assignment: Project Three
 * Application Name: "WeightTracker"
 * Option 3 - Weight Tracking App
 * University: SNHU
 */

//***Package for Weight Tracker***
package com.example.michaelkingweighttracker;

//***Java/Android Imports***
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import java.util.ArrayList;
import java.util.List;

//***Class Weight Database***
public class WeightDAO {

    //***Implement Database Helper***
    private final WeightDatabaseHelper dbHelper;

    //***Implement WeightDatabaseHelper for This Class***
    public WeightDAO(Context context) {
        dbHelper = new WeightDatabaseHelper(context);
    }

    //***Initiate CRUD Operations for Weight Entries***
    //***(Create, Read, Update, and Delete)***

    //CREATE method
    public void addEntry(String date, double weight) {
        //Declare SQLite Database
        SQLiteDatabase db = dbHelper.getWritableDatabase();
        //Declare Values for Database
        ContentValues values = new ContentValues();
        values.put(WeightDatabaseHelper.columnDate, date); //column Date
        values.put(WeightDatabaseHelper.columnWeight, weight); //column Date
        db.insert(WeightDatabaseHelper.tbWeight, null, values); //table Weight
        db.close(); //Closes the Database
    }//end CREATE method

    //READ method
    public List<WeightEntry> getAllEntries() {
        //Declare Array of Weight Entries
        List<WeightEntry> entries = new ArrayList<>();
        //Declare SQLite Database
        SQLiteDatabase db = dbHelper.getReadableDatabase();
        //Updates Weight Entry
        Cursor cursor = db.query(
                WeightDatabaseHelper.tbWeight, null, null,
                null, null, null,
                WeightDatabaseHelper.columnDate + " Desc"
        );
        //Moves the Cursor to the First Row
        if (cursor.moveToFirst()) {
            do { //Add Column ID, Date, and Weight to Entry
                long id = cursor.getLong(cursor.getColumnIndexOrThrow(WeightDatabaseHelper.columnID));
                String date = cursor.getString(cursor.getColumnIndexOrThrow(WeightDatabaseHelper.columnDate));
                double weight = cursor.getDouble(cursor.getColumnIndexOrThrow(WeightDatabaseHelper.columnWeight));
                entries.add(new WeightEntry(id, date, weight));
            } while (cursor.moveToNext());
        }//end if
        cursor.close(); //Closes the Cursor
        db.close(); //Closes the Database
        return entries; //Returns Weight Entries
    }//END READ method

    //UPDATE
    public void updateEntry(long id, String date, double weight) {
        //Declare SQLite Database
        SQLiteDatabase db = dbHelper.getWritableDatabase();
        //Declare Values for Database
        ContentValues values = new ContentValues();
        values.put(WeightDatabaseHelper.columnDate, date);
        values.put(WeightDatabaseHelper.columnWeight, weight);
        //Updates Weight Entry
        db.update(WeightDatabaseHelper.tbWeight, values,
                WeightDatabaseHelper.columnID + "=?",
                new String[]{String.valueOf(id)});
        db.close(); //close the Database
    }//end UPDATE method

    //DELETE
    public void deleteEntry(long id) {
        //Declare SQLite Database
        SQLiteDatabase db = dbHelper.getWritableDatabase();
        //Deletes Weight Entry
        db.delete(WeightDatabaseHelper.tbWeight,
                WeightDatabaseHelper.columnID + "=?",
                new String[]{String.valueOf(id)});
        db.close(); //close the Database
    }//end DELETE method

    //***Implement User Methods (Add, Validate)***

    //ADD USER TO DATABASE
    public long addUser(String username, String password) {
        //Declare SQLite Database
        SQLiteDatabase db = dbHelper.getWritableDatabase();
        //Declare Values for Database
        ContentValues values = new ContentValues();
        values.put(WeightDatabaseHelper.columnUsername, username);
        values.put(WeightDatabaseHelper.columnPassword, password);
        long id = db.insert(WeightDatabaseHelper.tbUsers, null, values);
        db.close(); //close the Database
        return id;
    }//end ADD USER method

    //Ensure that the User is Valid
    public boolean validateUser(String username, String password) {
        SQLiteDatabase db = dbHelper.getWritableDatabase();
        Cursor cursor = db.query(WeightDatabaseHelper.tbUsers, null,
                WeightDatabaseHelper.columnUsername + "=? And " +
                WeightDatabaseHelper.columnPassword + "=?",
                new String[]{username, password}, null,null,null);
        boolean valid = cursor.getCount() > 0;
        cursor.close(); //Closes the Cursor
        db.close(); //close the Database
        return valid; //User Returns as Valid
    }//end validate USER method

    //Set the Weight Goal
    public void setGoalWeight(String username, double goalWeight) {
        //Declare SQLite Database
        SQLiteDatabase db = dbHelper.getWritableDatabase();
        //Declare Values for Database
        ContentValues values = new ContentValues();
        values.put(WeightDatabaseHelper.columnGoalWeight, goalWeight);
        db.update(WeightDatabaseHelper.tbUsers, values,
                WeightDatabaseHelper.columnUsername + "=?",
                new String[]{username});
        db.close(); //close the Database
    }

    //Get the Weight Goal
    public double getGoalWeight (String username) {
        SQLiteDatabase db = dbHelper.getReadableDatabase();
        Cursor cursor = db.query(WeightDatabaseHelper.tbUsers,
                new String[]{WeightDatabaseHelper.columnGoalWeight},
                WeightDatabaseHelper.columnUsername + "=?", new String[]{username},
                null, null, null);
        double goal = -1;
        if (cursor.moveToFirst()) {
            goal = cursor.getDouble(0);
        }
        cursor.close(); //Closes the Cursor
        db.close(); //close the Database
        return goal; //Returns the Goal
    }//END GETTER
}//end class
