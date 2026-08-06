/*****CODE INFORMATION*****
 * Name: Michael King
 * Date: 2/22/2026
 * File: SmsNotificationHelper.java
 * Assignment: Project Three
 * Application Name: "WeightTracker"
 * Option 3 - Weight Tracking App
 * University: SNHU
 */

//***Package for Weight Tracker***
package com.example.michaelkingweighttracker;

//***Java/Android Imports***
import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import android.telephony.SmsManager;
import android.util.Log;
import android.widget.Toast;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import java.util.List;

//***Class for Sending SMS Notifications***
public class SmsNotificationHelper {

    //Declares SMS Permission Code.
    //This allows the app to request permission to send SMS messages
    public static final int smsPermissionCode = 101;
    public static final String TAG = "SMSNotificationHelper";
    private static String pendingMessage = null;

    //Call this Method to ensure Goal is Reached
    public static void checkAndNotify(Context context,
                                      String username,
                                      WeightDAO dao) {
        //Implement Weight Goal
        double goalWeight = dao.getGoalWeight(username);
        Log.d(TAG, "Goal Weight :" + goalWeight);

        //Skips SMS message if no goal weight is set
        if (goalWeight <= 0) {
            Log.d(TAG, "No goal weight set, skipping SMS.");
            return; //No goal set
        }//end if

        //Get All Weight Entries
        List<WeightEntry> entries = dao.getAllEntries();
        if (entries.isEmpty()) return;

        //Get Latest Weight Entry
        double latestWeight = entries.get(0).getWeight();
        Log.d(TAG, "Latest weight: "+latestWeight+", Goal: "+goalWeight);

        //Sends User a congratulations message if weight goal is reached
        if (latestWeight <= goalWeight) {
            String message = "Congratulations! You have reached your goal of "
                    +goalWeight+ " lbs! Current weight: "+latestWeight+" lbs.";
            requestAndSendSMS(context, message);
        }else { //Sends User a message if goal is not reached.
            Log.d(TAG, "Goal not yet reached.");
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
