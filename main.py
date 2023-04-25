import os
import requests
import openai

# Step 1: Import necessary libraries



openai.api_key = [enter your openAI API key here]

def get_nutrition_info(food_id):
  """Retrieves nutrition information for a given food item."""
  url = f"https://api.nutritionix.com/v1_1/item?id={food_id}&appId=[enter your nutritionix appID here]&appKey=[enter your nutritionix appKey here]"
  response = requests.get(url)
  return response.json()


def search_food_items(query):
  """Searches for food items based on a search query."""
  url = f"https://api.nutritionix.com/v1_1/search/{query}?results=0:20&fields=item_name,brand_name,item_id,nf_calories,nf_total_fat,nf_saturated_fat,nf_cholesterol,nf_sodium,nf_total_carbohydrate,nf_dietary_fiber,nf_sugars,nf_protein&appId=98995298&appKey=93ed1839727a9d7516838b5a16dfb07e"
  response = requests.get(url)
  return response.json()["hits"]


def generate_response(health_data, food_option, allergen_data, nutrition_info, username):
  """Generates a response using the ChatGPT model."""
  prompt = f"You are an expert medical nutritionist creating a health score for a menu item. You calculate this score by considering details about the user, including health history, and comparing these details to the nutrition facts about the menu item. You also take into consideration the establishment from which the client is ordering the food. These health scores are personalized to that particular client using the details they provide. These are the details you are considering: The username is {username} and this user has the following chronic health conditions: {health_data}, the user has these allergies: {allergen_data} and is interested in the following restauraunt: {food_option}. Here is a library of data for the food option from the restaurants menu: {nutrition_info}. Make a precise and specific health score for each and every food item on the menu for the specified restaurant on a scale of 0.0 - 10.0 based on the users health conditions provided. Make a health score for the “Menu Item” based on the conditions provided. These are some conditions to follow when providing a health score: The health score should be on a 2.0 - 10 scale. If the menu item contains an allergen the user has listed, the menu item should automatically be rated a 2.0. All items that do not contain an allergen should be rated between 3.0 - 9.9. Menu items that are particularly healthy for clients with cardiovascular disease, diabetes, and/or nutrient deficiencies should be rated between 6.0 - 9.9, unless the item contains an allergen. Menu items that are unhealthy for clients with cardiovascular disease, diabetes, and/or nutrient deficiencies should be rated between 2.1 - 5.9, unless the item contains an allergen. Be accurate and use all existing knowledge about the menu items as they pertain to the health conditions and details of this client to make the score. Provide the health score in this example format: “(5.5/10)” Also provide a recommendation, much like a nutritionist would provide to a client. Print the information in a similar format to the following: Scale:0.0 - Do not eat 10.0 - Perfectly healthy 1. [menu item]: Health Score [health score]/10 [explanation]. 2. [menu item]..."

  # Get the user's health data from the database.
  with open("users.txt", "r") as f:
    users = f.readlines()
    for user in users:
      if user.split(":")[0] == username:
        compressed_health_conditions = user.split(":")[1]
        break

  # Generate a personalized response based on the user's health data.
  response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.7,
    # compressed_health_conditions=compressed_health_conditions,
  )
  return response.choices[0].text.strip()



def main():
  """Prompts user for health data and food option, and generates a response."""

  # Check if user is logged in
  while True:
    print("Do you have an account? (Y/N)\r\n")
    response = input()
    if response == "Y":
      username = input("Please enter your username: \r\n")
      password = input("Please enter your password: \r\n")

      # Check if username and password are valid
      with open("users.txt", "r") as f:
        users = f.readlines()
        for user in users:
          if user.split(":")[0] == username:
            if user.split(":")[1] == password:
              print("Logged in successfully! Welcome back, " + username)
              break
        else:
          print("Invalid username or password.")
          continue
      break
    elif response == "N":
      print("Please create an account.")
      username = input("Please enter a username: \r\n")
      password = input("Please enter a password: \r\n")

      # Check if username is already taken
      with open("users.txt", "r") as f:
        users = f.readlines()
        for user in users:
          if user.split(":")[0] == username:
            print("Username is already taken. Please choose another one.")
            username = input("Please enter a username: \r\n")
            break

      # Add new user to file
      with open("users.txt", "a") as f:
        f.write(username + ":" + password + ":" + input("What chronic health conditions do you have? \r\n") + "," + input("Do you have any allergies?(Type None if no allergies) \r") + "\n")
      print("Account created successfully!")
      break
    else:
      print("Invalid input. Please try again.")

  # Prompt user for restaurant and get chronic health conditions and allergen information from the users.txt file
  food_option = input("What restaurant are you interested in? \r\n")
  with open("users.txt", "r") as f:
    users = f.readlines()
    for user in users:
      if user.split(":")[0] == username:
        health_data = user.split(":")[2].split(",")[0]
        allergen_data = user.split(":")[2].split(",")[1]
        break

  # Search for food items based on user input
  food_items = search_food_items(food_option)
  if len(food_items) == 0:
    print("No food items found.")
    return

  # Get nutrition information for the first 5 food items
  for i in range(5):
    food_item = food_items[i]
    nutrition_info = get_nutrition_info(food_item["fields"]["item_id"])

    # Generate a response using the ChatGPT model
    response = generate_response(health_data, food_option, allergen_data, nutrition_info, username)
    print("Based on your history of " + health_data + " and " + allergen_data+" allergy, " )
    print(response)

  # Prompt user to select another restaurant or see more food options from the same restaurant
  while True:
    print("Would you like to select a different restaurant? (Y/N)")
    response = input()
    if response == "Y":
      main()
      break
    elif response == "N":
      break
    else:
      print("Invalid input. Please try again.")


if __name__ == "__main__":
  main()
