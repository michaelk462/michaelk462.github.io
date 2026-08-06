/*****CODE INFORMATION*****
 * Name: Michael King
 * File: WeightDisplayActivity.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Enhancement Notes ---
 * All data access now goes through WeightApiService (Retrofit)
 * against the Flask/MongoDB backend instead of WeightDAO/SQLite.
 * Retrofit callbacks land back on the main thread by default, so UI updates
 * inside onResponse() are safe without an extra runOnUiThread() call.
 */

//***Package for Weight Tracker Enhancement***
package com.example.cs360enhancement;

//***Java, Android and Retrofit Imports***
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

import com.example.cs360enhancement.models.GoalDto;
import com.example.cs360enhancement.models.WeightEntryDto;
import java.util.Collections;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

//***Package for Displaying Weight***
public class WeightDisplayActivity extends AppCompatActivity{

    //Declare Variables and Other Java Classes
    private WeightApiService apiService;
    private WeightAdapter adapter;
    private double lastKnownGoal = -1;

    //***Method that Displays Weight Entries***
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //Activates Weight Entry UI Screen Layout
        setContentView(R.layout.activity_weight_display);

        //Declares current username
        String currentUsername = getIntent().getStringExtra("username");
        if (currentUsername == null) currentUsername = "";// safe default

        //Implements Weight Database for This Class
        apiService = ApiClient.getService(this);

        //Implements RecyclerView
        RecyclerView recyclerView = findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new GridLayoutManager(this, 2));

        //Gets All Weight Entries and WeightAdapter
        adapter = new WeightAdapter(Collections.emptyList(), new WeightAdapter.OnItemClickListener() {
            //Activates Edit and Delete Actions from Other Java Classes
            @Override
            //Edit Weight Entry
            public void onEditClick(WeightEntryDto entry) {
                showEditDialog(entry);
            }
            @Override
            //Delete Weight Entry
            public void onDeleteClick(WeightEntryDto entry) {
                deleteEntry(entry);
            }//end Adapter
        });//end void
        recyclerView.setAdapter(adapter);

        //Implements Add Button
        ImageButton imageButton = findViewById(R.id.buttonAddEntry);
        imageButton.setOnClickListener(v -> showAddDialog());

        loadGoal();
        loadEntries();
    }//end method

    //***Method to Load Weight Goals***
    private void loadGoal() {
        apiService.getGoal().enqueue(new Callback<>() {
            @Override
            public void onResponse(@NonNull Call<GoalDto> call, @NonNull Response<GoalDto> response) {
                if (response.isSuccessful() && response.body() != null) {
                    lastKnownGoal = response.body().getGoalWeight();
                    updateGoalDisplay(lastKnownGoal);
                }//end if
            }//end onResponse

            @Override
            public void onFailure(@NonNull Call<GoalDto> call, @NonNull Throwable t) {
                Toast.makeText(WeightDisplayActivity.this,
                        "Could not load goal: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }//end method

    //***Method to Load Weight Entries***
    private void loadEntries(){
        apiService.getEntries().enqueue(new Callback<>() {
            @Override
            public void onResponse(@NonNull Call<List<WeightEntryDto>> call, @NonNull Response<List<WeightEntryDto>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    adapter.updateData(response.body());
                } else {
                    Toast.makeText(WeightDisplayActivity.this,
                            "Could not load entries.", Toast.LENGTH_SHORT).show();
                }//end if
            }

            @Override
            public void onFailure(@NonNull Call<List<WeightEntryDto>> call, @NonNull Throwable t) {
                Toast.makeText(WeightDisplayActivity.this,
                        "Could not reach server: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }//end method

    //Re-fetches entries and, once they're back, checks the SMS goal
    //notification against the latest entry.
    private void refreshAndNotify() {
        apiService.getEntries().enqueue(new Callback<>() {
            @Override
            public void onResponse(@NonNull Call<List<WeightEntryDto>> call, @NonNull Response<List<WeightEntryDto>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    adapter.updateData(response.body());
                    if (!response.body().isEmpty()) {
                        double latestWeight = response.body().get(0).getWeight();
                        SmsNotificationHelper.checkAndNotify(
                                WeightDisplayActivity.this, lastKnownGoal, latestWeight);
                    }//end if
                }//end if
            }

            @Override
            public void onFailure(@NonNull Call<List<WeightEntryDto>> call, @NonNull Throwable t) {
                Toast.makeText(WeightDisplayActivity.this,
                        "Could not reach server: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }//end method

    //***Method to Show "Add Weight Entry" Dialog***
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
                        addEntry(date, Double.parseDouble(weightStr));
                    } //end if
                }) //set Positive Button
                .setNegativeButton("Cancel", null) //Cancel Button
                .show(); //displays dialog
    }//end method

    //***Method to Add Weight Entry***
    private void addEntry(String date, double weight) {
        apiService.addEntry(new WeightEntryDto(date, weight)).enqueue(new Callback<>() {
            @Override
            public void onResponse(@NonNull Call<WeightEntryDto> call, @NonNull Response<WeightEntryDto> response) {
                if (response.isSuccessful()) {
                    refreshAndNotify();
                } else {
                    Toast.makeText(WeightDisplayActivity.this,
                            "Could not add entry (Check date/weight format).", Toast.LENGTH_LONG).show();
                }//end if
            }

            @Override
            public void onFailure(@NonNull Call<WeightEntryDto> call, @NonNull Throwable t) {
                Toast.makeText(WeightDisplayActivity.this,
                        "Could not reach server: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }//end method


    //***Method to Show "Edit Weight Entry" Dialog***
    private void showEditDialog(WeightEntryDto entry) {
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
                        updateEntry(entry.getId(), date, Double.parseDouble(weightStr));
                    }//end if
                })//end Positive Button
                .setNegativeButton("Cancel", null) //Cancel Button
                .show(); //displays dialog
    }//end method

    //***Method to Update Weight Entry***
    private void updateEntry(String id, String date, double weight) {
        apiService.updateEntry(id, new WeightEntryDto(date, weight)).enqueue(new Callback<>() {
            @Override
            public void onResponse(@NonNull Call<WeightEntryDto> call, @NonNull Response<WeightEntryDto> response) {
                if (response.isSuccessful()) {
                    refreshAndNotify();
                } else {
                    Toast.makeText(WeightDisplayActivity.this,
                            "Could not update entry.", Toast.LENGTH_LONG).show();
                }//end if
            }

            @Override
            public void onFailure(@NonNull Call<WeightEntryDto> call, @NonNull Throwable t) {
                Toast.makeText(WeightDisplayActivity.this,
                        "Could not reach server: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }//end method

    //***Method to Delete Weight Entry***
    private void deleteEntry(WeightEntryDto entry) {
        apiService.deleteEntry(entry.getId()).enqueue(new Callback<>() {
            @Override
            public void onResponse(@NonNull Call<Void> call, @NonNull Response<Void> response) {
                if (response.isSuccessful()) {
                    refreshAndNotify();
                } else {
                    Toast.makeText(WeightDisplayActivity.this,
                            "Could not delete entry.", Toast.LENGTH_LONG).show();
                }//end if
            }

            @Override
            public void onFailure(@NonNull Call<Void> call, @NonNull Throwable t) {
                Toast.makeText(WeightDisplayActivity.this,
                        "Could not reach server: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }//end method

    //*** Method to Use Options Menu ***
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_weight_display, menu);
        return true;
    }//end method

    //*** Method to Use Goal Dialog ***
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

        if (lastKnownGoal > 0) {
            editTextGoalWeight.setText(String.valueOf(lastKnownGoal));
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
                        setGoal(Double.parseDouble(goalStr));
                    } else { //Displays message if no goal weight is entered
                        Toast.makeText(this, "Please enter a goal weight", Toast.LENGTH_LONG).show();
                    }//end if
                })//end Positive Button
                .setNegativeButton("Cancel", null) //Cancel Button
                .show(); //displays dialog
    }//end method

    private void setGoal(double goal) {
        apiService.setGoal(new GoalDto(goal)).enqueue(new Callback<>() {
            @Override
            public void onResponse(@NonNull Call<GoalDto> call, @NonNull Response<GoalDto> response) {
                if (response.isSuccessful() && response.body() != null) {
                    lastKnownGoal = response.body().getGoalWeight();
                    updateGoalDisplay(lastKnownGoal);
                    Toast.makeText(WeightDisplayActivity.this,
                            "Goal set to " + lastKnownGoal + "lbs!", Toast.LENGTH_LONG).show();
                    refreshAndNotify();
                } else {
                    Toast.makeText(WeightDisplayActivity.this,
                            "Could not set goal.", +Toast.LENGTH_LONG).show();
                }//end if
            }

            @Override
            public void onFailure(@NonNull Call<GoalDto> call, @NonNull Throwable t) {
                Toast.makeText(WeightDisplayActivity.this,
                        "Could not reach server: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
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