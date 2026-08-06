/*****CODE INFORMATION*****
 * Name: Michael King
 * File: WeightAdapter.java
 * Date: 7/31/2026
 * Assignment: CS 499 Enhancement Three: Databases
 * University: SNHU
 * --- Enhancement Notes ---
 * Now binds WeightEntryDto (from the REST API) instead of the old
 * SQLite-backed WeightEntry model. Functionally unchanged otherwise;
 * click callbacks still hand the full entry back to the activity, which
 * now performs the edit/delete as an API call.
 */

//***Package for Weight Tracker Enhancement***
package com.example.cs360enhancement;

//***Java/Android Imports***
import android.annotation.SuppressLint;
import android.view.*;
import android.widget.ImageButton;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.cs360enhancement.models.WeightEntryDto;
import java.util.List;

//***Class for Weight Adapter***
//RecyclerView is used for large data sets, in this case, weight entries.
public class WeightAdapter extends RecyclerView.Adapter<WeightAdapter.ViewHolder> {

    //***Declares Edit and Delete functions for weight entries***
    public interface OnItemClickListener {
        void onEditClick(WeightEntryDto entry); //edit weight entry
        void onDeleteClick(WeightEntryDto entry); //delete weight entry
    }//end method

    //***Declares Array List of Weight Entries***
    private List<WeightEntryDto> entries;
    private final OnItemClickListener listener;

    //***Method to declare usage of WeightAdapter and its variables***
    public WeightAdapter(List<WeightEntryDto> entries, OnItemClickListener listener) {
        this.entries = entries;
        this.listener = listener;
    }//end method

    //***Method to Implement ViewHolder, allowing the user to add weight entry***
    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int ViewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_weight_entry, parent, false);
        return new ViewHolder(view);
    }//end method

    //***Method to Represent Date, Weight Texts and Edit, Delete Buttons***
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        WeightEntryDto entry = entries.get(position);
        holder.textViewDate.setText(entry.getDate());
        holder.textViewWeight.setText(String.format("%s lbs", entry.getWeight()));
        holder.buttonEdit.setOnClickListener(v -> listener.onEditClick(entry));
        holder.buttonDelete.setOnClickListener(view -> listener.onDeleteClick(entry));
    }//end method

    //***Method that Returns the Number of Weight Entries***
    @Override
    public int getItemCount() { return entries.size(); }

    //***Method that Updates Weight Data***
    @SuppressLint("NotifyDataSetChanged")
    public void updateData(List<WeightEntryDto> newEntries) {
        this.entries = newEntries;
        notifyDataSetChanged();
    }//end method

    //***Method to Extend RecyclerView for Large Weight Entry Set***
    public static class ViewHolder extends RecyclerView.ViewHolder {
        public TextView textViewDate, textViewWeight; //declare TextView variables
        public ImageButton buttonEdit, buttonDelete; //declare Edit and Delete Buttons

        //Implement Texts and Buttons in ViewHolder
        public ViewHolder(View itemView) {
            super(itemView);
            textViewDate = itemView.findViewById(R.id.textViewDate);     //Date
            textViewWeight = itemView.findViewById(R.id.textViewWeight); //Weight
            buttonEdit = itemView.findViewById(R.id.buttonEdit);         //Edit Weight Entry
            buttonDelete = itemView.findViewById(R.id.buttonDelete);     //Delete Weight Entry
        }//end ViewHolder
    }//end class
}//end class
