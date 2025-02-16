#!/bin/bash

DIR="./data/accounts"

# Print the header with nice formatting
echo -e "Email\t\t\t     Points\tTimer"
echo -e "-----------------------------------------------------"

# Collect data to create a structured format for column
output=""

for file in "$DIR"/*; do
    if [[ -f $file ]]; then
        email=$(awk -F= '/^Email=/{print $2}' "$file")
        earnings=$(awk -F= '/^Points=/{print $2}' "$file")
        timer=$(awk -F= '/^Timer=/{print $2}' "$file")
        if [[ -n $email && -n $earnings ]]; then
            output+="$email\t$earnings\t\t$timer\n"
        fi
    fi
done

# Use column to format the output and sort by Total_Earnings
echo -e "$output" | sort -k2,2n | column -t -s $'\t'
echo -e "-----------------------------------------------------"
filename='./data/accounts/stopped_accounts.txt'
if [ -e "$filename" ]; then
  echo -e "Stopped accounts:"
  cat filename
  echo -e "-----------------------------------------------------"
fi

