/*****CODE INFORMATION*****
 * Name: Michael King
 * File: LoginActivity.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Enhancement Notes ---
 * checkAndNotify() no longer takes a WeightDAO;
 * Data now comes from asynchronous Retrofit calls, so the caller
 * supplies the goal weight and latest weight it already retrieved
 * from the API rather than this class querying a database itself.
 */

//***Package for Weight Tracker***
package com.example.cs360enhancement;

//***Java/Android Imports***
import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.telephony.SmsManager;
import android.util.Log;
import android.widget.Toast;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

//***Class for Sending SMS Notifications***
public class SmsNotificationHelper {

    //Declares SMS Permission Code.
    //This allows the app to request permission to send SMS messages
    public static final int smsPermissionCode = 101;
    public static final String TAG = "SMSNotificationHelper";
    private static String pendingMessage = null;

    // Tracks which goal value the user was last congratulated for, so
    // checkAndNotify() doesn't re-send the same text on every subsequent
    // add/edit/delete while the user is still under the same goal.
    private static final String NOTIFY_PREFS = "sms_notify_state";
    private static final String KEY_LAST_NOTIFIED_GOAL = "last_notified_goal";


    //Call this Method to ensure Goal is Reached
    public static void checkAndNotify(Context context,
                                      double goalWeight,
                                      double latestWeight) {
        //Implement Weight Goal
        //double goalWeight = dao.getGoalWeight(username);
        Log.d(TAG, "Goal Weight :" + goalWeight + ", Latest Weight: " + latestWeight);

        //Skips SMS message if no goal weight is set
        if (goalWeight <= 0) {
            Log.d(TAG, "No goal weight set, skipping SMS.");
            return; //No goal set
        }//end if

        SharedPreferences prefs = context.getSharedPreferences(NOTIFY_PREFS, Context.MODE_PRIVATE);
        float lastNotifiedGoal = prefs.getFloat(KEY_LAST_NOTIFIED_GOAL, -1f);

        //Sends User a congratulations message if weight goal is reached
        if (latestWeight <= goalWeight) {
            String message = "Congratulations! You have reached your goal of "
                    +goalWeight+ " lbs! Current weight: "+latestWeight+" lbs.";
            requestAndSendSMS(context, message);
        }else { //Sends User a message if goal is not reached.
            Log.d(TAG, "Goal not yet reached.");
            //Clear so a fresh "goal reached" text can fire again later if
            //the user's weight climbs back above goal and drops again.
            if (lastNotifiedGoal != -1f) {
                prefs.edit().remove(KEY_LAST_NOTIFIED_GOAL).apply();
            }
        }//end if
    }//end method

    //Method to Request SMS Permission
    public static void requestAndSendSMS(Context context, String message) {
        //If permission is granted, the SMS messages will be sent
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.SEND_SMS)
            == PackageManager.PERMISSION_GRANTED) {
            Log.d(TAG, "SMS Permission Granted, Sending Message.");
            sendSMS(context, message);
        }else {
            //Request SMS Permissions
            Log.d(TAG, "SMS Permission Not Granted. Requesting...");
            pendingMessage = message;
            if (context instanceof Activity) {
                ActivityCompat.requestPermissions((Activity) context,
                        new String[]{Manifest.permission.SEND_SMS},
                        smsPermissionCode);
            }//end if
        }//end if
    }//end method

    public static void sendSMS(Context context, String message) {
        //Sending SMS is simulated in the Android Emulator.
        //In the real app, the user's phone number is retrieved from
        //the database.
        String phoneNumber = "(650) 555-1212"; //fake phone number
        try { //Sends User SMS Notification
            SmsManager smsManager;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                smsManager = context.getSystemService(SmsManager.class);
            } else {
                smsManager = SmsManager.getDefault();
            }//end if

            //If SMS Manager is Null, display message
            if (smsManager == null) {
                Log.e(TAG, "SmsManager is Null");
                Toast.makeText(context, "SMS Service Unavailable", Toast.LENGTH_SHORT).show();
                return;
            }//end if
            //Sends User SMS Notification if Goal is Reached
            smsManager.sendTextMessage(phoneNumber, null, message, null, null);
            Log.d(TAG, "SMS Sent Successfully to "+phoneNumber);
            Toast.makeText(context, "Goal Reached! SMS alert sent!", Toast.LENGTH_LONG).show();
        } catch (Exception e) { //Sends Error Message if SMS Notification is Not Sent
            Log.d(TAG, "SMS Failed to Send: " + e.getMessage());
            Toast.makeText(context, "SMS Notification Failed to Send + " + e.getMessage(), Toast.LENGTH_LONG).show();
        }//end try/catch
    }//end method

    // Method is called from WeightDisplayActivity.java
    public static void onPermissionResult(Context context, int[] grantResults) {
        if (grantResults.length > 0 && grantResults[0] ==
                PackageManager.PERMISSION_GRANTED) {
            Log.d(TAG, "SMS permission granted by user.");
            if (pendingMessage != null) {
                sendSMS(context, pendingMessage);
                pendingMessage = null;
            }//end if
        } else {
            Log.d(TAG, "SMS permission denied by user.");
            Toast.makeText(context,
                    "SMS Permission Denied. Notifications Disabled but app will continue normally.",
                    Toast.LENGTH_LONG).show();
        }//end if
    }//end method
}//end class
