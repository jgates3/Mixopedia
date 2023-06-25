import tkinter as tk
from PIL import ImageTk, Image
import requests
import io
import webbrowser
import pandas as pd


class Mixopedia:
    def __init__(self):
        self.default_measures = None
        self.default_ingredients = None
        self.dutch_button = None
        self.italian_button = None
        self.random_button = None
        self.buy_button = None
        self.video_button = None
        self.instructions_text = None
        self.info_text = None
        self.image_label = None
        self.placeholder_img = None
        self.button = None
        self.entry = None
        self.label = None
        self.window = tk.Tk()
        self.window.title("Mixopedia")
        self.window.geometry("500x630")
        self.window.resizable(False, False)
        self.df = pd.read_csv('alcohol_list.csv', encoding='utf-8')
        self.create_UI()

    def create_UI(self):
        self.label = tk.Label(self.window, text="Enter a drink name:")
        self.label.pack()

        self.entry = tk.Entry(self.window)
        self.entry.pack()

        self.button = tk.Button(self.window, text="Search", command=self.search_drink)
        self.button.pack()

        self.image_label = tk.Label(self.window)
        self.image_label.pack()

        self.placeholder_img = Image.new("RGB", (250, 250), "lightgray")
        self.placeholder_img = ImageTk.PhotoImage(self.placeholder_img)
        self.image_label = tk.Label(self.window, image=self.placeholder_img)
        self.image_label.pack()

        self.info_text = tk.Text(self.window, height=2, width=50)
        self.info_text.config(state=tk.DISABLED)
        self.info_text.pack()

        self.instructions_text = tk.Text(self.window, height=10, width=50)
        self.instructions_text.config(state=tk.DISABLED)
        self.instructions_text.pack()

        self.video_button = tk.Button(self.window, text="Load Video", state=tk.DISABLED)
        self.video_button.pack()

        self.buy_button = tk.Button(self.window, text="Buy Drink", state=tk.DISABLED)
        self.buy_button.pack()

        self.italian_button = tk.Button(self.window, text="Italian", state=tk.DISABLED)
        self.italian_button.pack(side=tk.RIGHT)

        self.dutch_button = tk.Button(self.window, text="Dutch", state=tk.DISABLED)
        self.dutch_button.pack(side=tk.RIGHT)

        self.random_button = tk.Button(self.window, text="Random", command=self.random_drink)
        self.random_button.pack(side=tk.LEFT)

    def random_drink(self):
        random_string = self.df["DRINK NAME"].sample(n=1).values[0]
        self.entry.delete(0, tk.END)
        self.entry.insert(tk.END, random_string)
        self.search_drink()

    def get_apidata(self, drink_name):
        url = f"http://www.thecocktaildb.com/api/json/v1/1/search.php?s={drink_name}"
        response = requests.get(url)
        data = response.json()
        return data

    def search_drink(self):
        ingredients = []
        measures = []
        drink_name = self.entry.get()
        data = self.get_apidata(drink_name)

        if 'drinks' in data:  # if the searched drinks is in the drinks api
            new_drink = data['drinks'][0]  # find drink in drink api
            instructions = new_drink.get('strInstructions')  # get instructions
            for i in range(1, 16):  # loops to get ingredients. (since drinks typically use at most 15 ingredients.)
                ingredient = new_drink.get(f'strIngredient{i}')  # gets ingredient of selected drink
                measure = new_drink.get(f'strMeasure{i}')  # gets measure of selected drink
                if ingredient and measure:  # if measurements and ingredients arent null
                    ingredients.append(ingredient)  # append ingredients
                    measures.append(measure)  # append measurements

            self.get_info(new_drink)
            self.get_instructions(instructions, ingredients, measures)
            self.get_image(new_drink.get('strDrinkThumb'))
            self.get_video_button(new_drink.get('strVideo'))
            self.get_lang_buttons(new_drink)
            self.get_description(drink_name)
            self.get_buy_drink_button(drink_name)
        else:
            self.get_error()

    def get_info(self, drink):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert(tk.END, "Alcoholic or Non-Alcoholic: ")
        self.info_text.insert(tk.END, drink.get('strAlcoholic'))  # gets info about if drink is alcoholic or not
        self.info_text.insert(tk.END, "\nGlass: ")
        self.info_text.insert(tk.END, drink.get('strGlass'))  # gets info about type of glass used
        self.info_text.config(state=tk.DISABLED)

    def get_description(self, drink_name):
        filter_process = self.df.loc[self.df['DRINK NAME'] == drink_name, 'DRINK DESCRIPTION']  # filters based on drink_name
        drink_desc_values = filter_process.values  # gets values from filter
        drink_desc = drink_desc_values[0]  # gets the first matching value

        print(drink_desc)
        if drink_desc != None:
            self.instructions_text.config(state=tk.NORMAL)
            self.instructions_text.insert(tk.END, f"\nDrink Description:\n{drink_desc}") #displays drink description
            self.instructions_text.config(state=tk.DISABLED)
        else:
            self.instructions_text.config(state=tk.NORMAL)
            self.instructions_text.insert(tk.END, "\nDrink Description:\nNo description found.") #no description found
            self.instructions_text.config(state=tk.DISABLED)

    def get_instructions(self, instructions, ingredients, measures):
        self.instructions_text.config(state=tk.NORMAL)
        self.instructions_text.delete('1.0', tk.END)
        self.instructions_text.insert(tk.END, "Instructions:\n") #displays instructions
        self.instructions_text.insert(tk.END, instructions)
        self.instructions_text.insert(tk.END, "\n\nIngredients:\n")
        total = len(ingredients) #gets the length of the ingredients
        for i in range(total):
            if ingredients[i]: #gets ingredients
                ingredient = ingredients[i]
            else:
                ingredient = " " #no ingredients

            if measures[i]: #gets measures
                measure = measures[i]
            else:
                measure = " " #no measurements

            if ingredient.strip() or measure.strip():
                self.instructions_text.insert(tk.END, f"{ingredient} {measure}\n") #displays ingredients and measurements

        self.instructions_text.config(state=tk.DISABLED)

    def get_image(self, image_url):
        response = requests.get(image_url) #gets image
        if response.status_code == 200: #if request is successful
            img_data = response.content
            img = Image.open(io.BytesIO(img_data)) #gets image from api
        else:
            img = Image.new("RGB", (250, 250), "lightgray")  # placeholder image if the image is not available (no internet case)

        img = img.resize((250, 250)) #resizes image
        img = ImageTk.PhotoImage(img)
        self.image_label.config(image=img)
        self.image_label.image = img

    def get_video(self, video_url):
        webbrowser.open_new_tab(video_url) #opens new tab to go to video

    def get_video_button(self, video_url):
        if video_url != None: #video found
            self.video_button.config(state=tk.NORMAL, command=lambda: self.get_video(video_url))
        else:
            self.video_button.config(state=tk.DISABLED) #no video

    def get_buy_drink(self, drink_name):
        buy_url = f"https://www.google.com/search?q={drink_name}&tbm=shop"
        webbrowser.open_new_tab(buy_url) #opens tab and redirects to google shopping page

    def get_buy_drink_button(self, drink_name):
        if drink_name != None: #link works
            self.buy_button.config(state=tk.NORMAL, command=lambda: self.get_buy_drink(drink_name))
        else: #links doesnt work
            self.buy_button.config(state=tk.DISABLED)

    def get_lang_buttons(self, drink):
        ingredients_en = [] #english ingredients
        measures_en = [] #english measurements
        italian_instruct = drink.get('strInstructionsIT') #get italian instructions
        dutch_instruct = drink.get('strInstructionsDE') #gets dutch instructions

        for i in range(1, 16):
            ingredient = drink.get(f'strIngredient{i}')
            ingredients_en.append(ingredient) #appends english ingredients
            measure = drink.get(f'strMeasure{i}')
            measures_en.append(measure) #appends english measure

        if italian_instruct != None:
            self.italian_button.config(state=tk.NORMAL,command=lambda: self.get_instructions(italian_instruct, ingredients_en, measures_en))
        else:
            self.italian_button.config(state=tk.DISABLED)

        if dutch_instruct != None:
            self.dutch_button.config(state=tk.NORMAL,command=lambda: self.get_instructions(dutch_instruct, ingredients_en, measures_en))
        else:
            self.dutch_button.config(state=tk.DISABLED)

    def get_error(self): #gets error if drink isnt found
        self.instructions_text.config(state=tk.NORMAL)
        self.instructions_text.delete('1.0', tk.END)
        self.instructions_text.insert(tk.END, "Drink not found.")
        self.instructions_text.config(state=tk.DISABLED)

    def run(self):
        self.window.mainloop()


app = Mixopedia()
app.run()
