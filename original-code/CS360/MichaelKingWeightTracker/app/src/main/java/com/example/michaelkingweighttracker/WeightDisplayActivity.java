/*****CODE INFORMATION*****
 * Name: Michael King
 * Date: 2/22/2026
 * File: WeightDisplayActivity.java
 * Assignment: Project Three
 * Application Name: "WeightTracker"
 * Option 3 - Weight Tracking App
 * University: SNHU
 */

//***Package for WeightTracker***
package com.example.michaelkingweighttracker;

//***Java/Android Imports***
import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

//***Package for Displaying Weight***
public class WeightDisplayActivity extends AppCompatActivity{

    //Declare Variables and Other Java Classes
    private WeightDAO weightDAO;
    private WeightAdapter adapter;
    private String currentUsername;

    //***Method that Displays Weight Entries***
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //Activates Weight Entry UI Screen Layout
        setContentView(R.layout.activity_weight_display);

        //Declares current username
        currentUsername = getIntent().getStringExtra("username");
        if (currentUsername == null) currentUsername = ""; // safe default

        //Implements Weight Database for This Class
        weightDAO = new WeightDAO(this);

        //Implements RecyclerView
        RecyclerView recyclerView = findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new GridLayoutManager(this, 2));

        double savedGoal = weightDAO.getGoalWeight(currentUsername);
        updateGoalDisplay(savedGoal);

        //Gets All Weight Entries and WeightAdapter
        List<WeightEntry> entries = weightDAO.getAllEntries();
        adapter = new WeightAdapter(entries, new WeightAdapter.OnItemClickListener() {
            //Activates Edit and Delete Actions from Other Java Classes
            @Override
            //Edit Weight Entry
            public void onEditClick(WeightEntry entry) {
                showEditDialog(entry);
            }
            @Override
            //Delete Weight Entry
            public void onDeleteClick(WeightEntry entry) {
                weightDAO.deleteEntry(entry.getId());
                refreshData();
                SmsNotificationHelper.checkAndNotify(WeightDisplayActivity.this,
                        currentUsername, weightDAO);
            }//end Adapter
        });//end void
        recyclerView.setAdapter(adapter);

        //Implements Add Button
        ImageButton imageButton = findViewById(R.id.buttonAddEntry);
        imageButton.setOnClickListener(v -> showAddDialog());
    }//end method


    //***Method to Add Weight Entry***
    private void showAddDialog() {
        //Implements dialogView from a separate XML file.
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_add_weight, null);

        //Declares Date and Weight variables for Dialog
        EditText editDialogDate = dialogView.findViewById(R.id.editDialogDate);
        EditText editDialogWeight = dialogView.findViewById(R.id.editDialogWeight);

        //***Sets Dialog to Add a Weight Entry***
        new AlertDialog.Builder(this)
                .setTitle("Add Weight Entry") //Title
                .setView(dialogView) //View Dialog
                //Add Button
                .setPositiveButton("Add", (dialog, which) -> {
                    String date = editDialogDate.getText().toString().trim(); //date
                    String weightStr = editDialogWeight.getText().toString().trim(); //weight
                    //If both date and weight are *not* empty,
                    //the weight entry is added.
                    if (!date.isEmpty() && !weightStr.isEmpty()) {
                        weightDAO.addEntry(date, Double.parseDouble(weightStr));
                        refreshData(); //Refreshes All Weight Data
                        SmsNotificationHelper.checkAndNotify(this, currentUsername, weightDAO);
                    } //end if
                }) //set Positive Button
                .setNegativeButton("Cancel", null) //Cancel Button
                .show(); //displays dialog
    }//end method

    //***Method to Edit Weight Entry***
    private void showEditDialog(WeightEntry entry) {
        //Implements dialogView from a separate XML file.
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_add_weight, null);

        //Declares Date and Weight variables for Dialog
        EditText editDialogDate = dialogView.findViewById(R.id.editDialogDate);
        EditText editDialogWeight = dialogView.findViewById(R.id.editDialogWeight);
        editDialogDate.setText(entry.getDate());
        editDialogWeight.setText(String.valueOf(entry.getWeight()));

        //***Sets Dialog to Edit a Weight Entry***
        new AlertDialog.Builder(this)
                .setTitle("Edit Weight Entry") //Title
                .setView(dialogView)
                //Save Button
                .setPositiveButton("Save", (dialog, which) -> {
                    String date = editDialogDate.getText().toString().trim(); //date
                    String weightStr = editDialogWeight.getText().toString().trim(); //weight
                    //If both date and weight are *not* empty,
                    //the weight entry is updated.
                    if (!date.isEmpty() && !weightStr.isEmpty()) {
                        weightDAO.updateEntry(entry.getId(), date, Double.parseDouble(weightStr));
                        refreshData(); //Refreshes All Weight Data
                        SmsNotificationHelper.checkAndNotify(this, currentUsername, weightDAO);
                    }//end if
                })//end Positive Button
                .setNegativeButton("Cancel", null) //Cancel Button
                .show(); //displays dialog
    }//end method

    //Method to Refresh All Weight Data
    private void refreshData() {
        adapter.updateData(weightDAO.getAllEntries());
    }

    //Method to Use menu_weight_display.xml File for This Class
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_weight_display, menu);
        return true;
    }//end method

    //Method to Use action_set_goal.xml File for This Class
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.action_set_goal) {
            showSetGoalDialog();
            return true;
        }//end if
        return super.onOptionsItemSelected(item);
    }//end method

    //Method to Show Dialog for Weight Goal
    private void showSetGoalDialog() {
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_set_goal, null);
        EditText editTextGoalWeight = dialogView.findViewById(R.id.editTextGoalWeight);

        double currentGoal = weightDAO.getGoalWeight(currentUsername);
        if (currentGoal > 0) {
            editTextGoalWeight.setText(String.valueOf(currentGoal));
        }//end if

        //***Sets Dialog to Set a Weight Goal***
        new AlertDialog.Builder(this)
                .setTitle("Set Goal Weight") //Title
                .setView(dialogView)
                //Save Button
                .setPositiveButton("Save", (dialog, which) -> {
                    String goalStr = editTextGoalWeight.getText().toString().trim(); //weight goal
                    //If both date and weight are *not* empty,
                    //the weight entry is updated.
                    if (!goalStr.isEmpty()) {
                        double goal = Double.parseDouble(goalStr);
                        weightDAO.setGoalWeight(currentUsername, goal);
                        updateGoalDisplay(goal);
                        SmsNotificationHelper.checkAndNotify(this, currentUsername, weightDAO);
                        Toast.makeText(this, "Goal set to "+goal+" lbs!", Toast.LENGTH_LONG).show();
                    } else {
                        Toast.makeText(this, "Please enter a goal weight", Toast.LENGTH_LONG).show();
                    }//end if
                })//end Positive Button
                .setNegativeButton("Cancel", null) //Cancel Button
                .show(); //displays dialog
    }//end method

    //Method to Update the Weight Goal
    @SuppressLint("SetTextI18n")
    private void updateGoalDisplay(double goal) {
        TextView textViewGoalWeight = findViewById(R.id.textViewGoalWeight);
        if (goal > 0) { //Displays message if weight goal is updated
            textViewGoalWeight.setText("Goal Weight: " + goal + " lbs");
        }else { //Displays Weight Goal that is not yet updated
            textViewGoalWeight.setText("Goal Weight: Not Set");
        }
    }

    //***Method to Handle SMS Permission Result***
    @Override
    public void onRequestPermissionsResult (int requestCode,
                                            @NonNull String[] permissions,
                                            @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        // If request Code is the same as SMS Permission Code,
        // SMS Permission is granted.
        if (requestCode == SmsNotificationHelper.smsPermissionCode) {
            SmsNotificationHelper.onPermissionResult(this, grantResults);
        }//end if
    }//end method
}//end class