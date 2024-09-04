# OreAtlas
#### Video Demo: https://youtu.be/_JZnELEhdCA
### Description:
OreAtlas is a Flask web application designed to visualize global mineral production data. This project was developed by Ryan McKay as a final project for *CS50's Introduction to Computer Science*. The app features interactive maps that allow users to explore production figures for various minerals around the globe.


### Features:
- **Interactive Maps:** Visualize global production data for 65 mineral commodities across 168 countries.
- **Mineral Categories:** Minerals are grouped into Ferro-Alloy Metals, Non-Ferrous Metals, Precious Metals, Industrial Minerals, and Mineral Fuels.
- **Responsive Design:** Navigate intuitively with mouseover and zoom functionality powered by Flask, Jinja, and Bootstrap.
- **Intuitive Statistics:** Engage with tooltips showing production in tonnes/kilograms and percent of global output. Countries are coloured according to the selected mineral category and production rank.


### Source Data:
- The source data are accessible on <a href="www.world-mining-data.info">*www.world-mining-data.info*</a> and in the annual publication "World Mining Data" by the Austrian Federal Ministry of Finance. Please consult their website for additional information. OreAtlas displays mining data for the year 2022.
- Icons were retrieved from the following webpages:
    - <a href="https://www.flaticon.com/free-icons/pickaxe">Pickaxe icon by Creaticca Creative Agency on Flaticon</a>
    - <a href="https://imgbin.com/png/f1HdtCWB/iron-ore-png">Rock icon by Pixel8UK on imgbin</a>
    - <a href="https://www.freepik.com/icon/mining-cart_10852588">Mining Cart by bsd on Freepik</a>
    - <a href="https://similarpng.com/gold-bars-golden-bricks-yellow-precious-metal-bullion-blocks-of-highest-standard-on-transparent-background-png/#getdownload">Gold bars icon by Ra20Ga on similarpng</a>
    - <a href="https://www.flaticon.com/free-icons/mining-truck">Mining truck icon by Freepik on Flaticon</a>
    - <a href="https://www.flaticon.com/free-icons/oil">Oil icon created by Freepik on Flaticon</a>



### Project File Structure:
- **6.5. Share_of_World_Mineral_Production_2022_by_Countries.xls** – Source mining data for 2022 in Excel format (processed using Pandas).
- **6.5. Share_of_World_Mineral_Production_2021_by_Countries.xls** – Mining data for 2021. Future iterations of the app may incorporate this and future datasheets.
- **app.py** - The main Flask application file.
- **Metal_template.py** - Template used for constructing each of the component mineral sections in the main app. See *'Design considerations'* below.
- **requirements.txt** - List of program requirements.
- **static/** – Directory for static files like CSS and images.
- **styles.css** – Custom CSS file for additional styling.
- **templates/** – Directory containing HTML templates for the landing page, layout, and each of the five mineral categories.
- **world-countries.json** – Countries and their geometries as sets of coordinates (processed using GeoPandas). Original file was modified to fill missing geometries and to ensure consistent country naming with the Excel data: e.g. added polygon coordinates of Bahrain, changed Swaziland to Eswatini, Czech Republic to Czechia, and 'The United States' to 'United States'.


### Code Structure:
The main functionalities of *OreAtlas* were written in Python using the Folium module. The app is organized into two main sections:
1. **Configuration Section:**
    1. Connects the app to Flask.
    2. Reads the Excel and JSON files using Pandas and GeoPandas, respectively, and stores the data in variables for later use.
    3. Defines the basemap and tooltip style properties that will be applied to each map.
    4. Creates a Dictionary for map storage. The 'Keys' of the Dictionary are populated from the names of the Excel sheet, corresponding to the names of mineral commodities. The Dictionary 'Value' is initially empty, but will store the final map for each mineral. Jinja syntax will then refer to this Dictionary to produce maps on each tab of the HTML layouts.

2. **Minerals Section:**
    - Comprises five functions corresponding to the main mineral categories:
        - ferro_alloy()
        - non_ferrous()
        - precious_metals()
        - industrial_minerals()
        - mineral_fuels()
    - Each function is subdivided into its component minerals. One mineral subdivision does the following:
        1. Generates a Folium map for the individual mineral and loads the basemap into it.
        2. Reads the specific Excel sheet corresponding to that mineral into a Pandas dataframe, and tells the dataframe to skip the first row (Headers) and ignore the last row (Totals).
        3. Merges the Mineral dataframe (Pandas) and the Countries geometry dataframe (GeoPandas), linking them by the country names.
        4. Defines the properties of a Folium "chloropleth" (i.e. colourmap visualization) by linking it to the merged dataframe and defining stylistic properties according to the mineral category. Adds the chloropleth to the Folium mineral map defined above.
        5. Defines the contents of the hover-tooltips by linking them to the merged dataframe. Also links to the base style properties defined in the Configuration Section. Adds the tooltip to the Folium mineral map.
        6. Stores the map data as the 'Value' in the key:value pair corresponding to the mineral.
    - Each category function ends with a "render_template" function, which finally connects all of the data into the appropriate HTML layout and refers to the Dictionary containing the maps.


### Design Considerations and Hurdles:
- **Jenks:** The exact color scale for each mineral is tailored to that mineral's specific production statistics by 'Natural Jenks', which means that even highly-skewed production will display an even distribution of shades across all the countries, making for a more informative visualization. However, Natural Jenks requires a minimum of six classes. Until I figured that out, it mysteriously did not work for 6 of the 65 minerals (the ones that are dominated by just a few countries). I turned off Natural Jenks for those countries such that the colour distribution is exactly even (by number), regardless of any skewedness of the data.
- **Iterable Maps:** The main hangup of this coding project was my attempt at shortening it into clean iterable code to generate each map. Currently, the project comprises 65 distinct sections — one for each mineral — but an early version of the code was just one section, employing for-loops and if-statements to define the correct properties of each map. I had trouble associating these maps to the tabs defined in the HTML layouts using Jinja. After weeks of struggle, I eventually abandoned iteration in favour of individual mineral sections, using a template.
- **Coding Template:** Changing the code to individual mineral sections ultimately only took a couple of hours thanks to a template I created. The base code can be found in the file *Metal_template.txt*. I used the word "METAL" in place of anywhere I'd reference a specific mineral's name. After modifying the template according to the main stylistic properties I desired (e.g. mineral category), I copied it into *app.py*. Once copied, I used VSCode's *'Change All Occurrences'* to change to the specific mineral name. Repeat 65 times.


### Future Improvements:
- **Mobile Compatibility:** The app could be better optimized for smaller devices. I have made a few tweaks for mobile viewing, like different instructional images in the 'About' section, and adding Full Screen mode so that maps viewable on a smaller devices. Without going into Full Screen, the mobile layout of maps is not the most functional.
- **Toggle Data** OreAtlas currently displays data for 2022, which is the most recent publication of data at the time of this writing (August 2024). I briefly attempted to add 2021 data as a toggleable field for each map, as this would allow the user to easily compare 2021 to 2022 production, but it proved to be a big project. I will save this for later, and consider adding other years as the data are published.
- **Additional visualizations:** The project would be enhanced by showing pie charts, stacked area charts, or other data visualizations to show the relative weight of each country in terms of global production. Further, the project could expand by accessing other datasets related to mining.
- **Personal Website:** I intend for OreAtlas to eventually be accessible at my personal website, which is in development.


### Installation
To run the OreAtlas web application locally, follow these steps:

**1. Install Python**
First, ensure that Python is installed on your computer.

- Check if Python is already installed:
    - Open a terminal (macOS/Linux) or command prompt (Windows).
    - Type the following command and press Enter:
        ```bash
        python --version
        ```
    - If Python is installed, you'll see a version number. If not, you'll need to install it.

- Install Python:
    - Download Python from the official Python website.
    - Follow the installation instructions specific to your operating system.
    - Ensure that you check the option to "Add Python to PATH" during the installation process.


**2. Clone the Repository**
Next, you'll need to clone the OreAtlas repository from GitHub. Cloning a repository means creating a local copy of the code on your computer.

- Navigate to the directory where you want to clone the repository:
    - macOS/Linux:
        - Open Terminal.
        - Use the 'cd' command to navigate to your desired directory. For example, if you want to clone the repository into a folder called Projects in your home directory, type:
            ```bash
            cd /Users/your-username/Projects
            ```
        - If the Projects directory doesn’t exist, create it first by typing:
            ```bash
            mkdir /Users/your-username/Projects
            cd /Users/your-username/Projects
            ```
    - Windows:
        - Open Command Prompt or PowerShell.
        - Use the 'cd' command to navigate to your desired directory. For example, to navigate to a Projects folder in your Documents directory, type:
            ```bash
            cd C:\Users\YourUsername\Documents\Projects
            ```
        - If the Projects directory doesn’t exist, create it first by typing:
            ```bash
            mkdir C:\Users\YourUsername\Documents\Projects
            cd C:\Users\YourUsername\Documents\Projects
            ```
    - Clone the repository:
        - Once you’re in the correct directory, clone the repository by typing:
            ```bash
            git clone https://github.com/rdmckay/OreAtlas.git
            ```
        - This command will create a folder named OreAtlas in the directory, containing all the files from the GitHub repository.

**3. Install Dependencies**
After cloning the repository, you'll need to install the required Python libraries (dependencies) that the application relies on.

- Navigate to the OreAtlas directory:
    - Use the cd command again to enter the OreAtlas directory:
        ```bash
        cd OreAtlas
        ```
- Set up a virtual environment (optional but recommended):
    - A virtual environment isolates your project's dependencies from your global Python installation, preventing conflicts.
    - Create a virtual environment by typing:
        ```bash
        python -m venv venv
        ```
    - Activate the virtual environment:
        - macOS/Linux:
            ```bash
            source venv/bin/activate
            ```
        - Windows:
            ```bash
            venv\Scripts\activate
            ```
    - Install the required dependencies:
        - With the virtual environment activated, install the dependencies using 'pip' (Python’s package manager):
            ```bash
            pip install -r requirements.txt
            ```
        - This command will read the requirements.txt file and install all the necessary packages.

**4. Run the Application**
Once the dependencies are installed, you can run the OreAtlas application.

- Start the Flask development server:
    - Ensure you’re still in the OreAtlas directory and your virtual environment is activated.
    - Run the application by typing:
        ```bash
        flask run
        ```
    - You should see output indicating that the server is running.
- Access the application:
    - Open a web browser and go to the address provided by Flask, typically http://127.0.0.1:5000/.
    - You should see the OreAtlas application running in your browser


### Mineral Commodities

#### Ferro-Alloy Metals:

- Iron (Fe)
- Chromium (Cr2O3)
- Cobalt (Co)
- Manganese (Mn)
- Molybdenum (Mo)
- Nickel (Ni)
- Niobium (Nb2O5)
- Tantalum (Ta2O5)
- Titanium (TiO2)
- Tungsten (W)
- Vanadium (V)

#### Non-Ferrous Metals:

- Aluminium (Al, primary)
- Antimony (Sb)
- Arsenic (As2O3)
- Bauxite (crude ore)
- Beryllium (concentrate)
- Bismuth (Bi)
- Cadmium (Cd)
- Copper (Cu)
- Gallium (Ga)
- Germanium (Ge)
- Indium (In)
- Lead (Pb)
- Lithium (Li2O)
- Mercury (Hg)
- Rare Earth Minerals (REO)
- Rhenium (Re)
- Selenium (Se)
- Tellurium (Te)
- Tin (Sn)
- Zinc (Zn)

#### Precious Metals:

- Gold (Au)
- Palladium (Pd)
- Platinum (Pt)
- Rhodium (Rh)
- Silver (Ag)

#### Industrial Minerals:

- Asbestos
- Baryte
- Bentonite
- Boron Minerals
- Diamonds (Gem) in ct
- Diamonds (Industrial) in ct
- Diatomite
- Feldspar
- Fluorspar
- Graphite
- Gypsum and Anhydrite
- Kaolin (China-Clay)
- Magnesite
- Perlite
- Phosphate Rock (P2O5)
- Potash (K2O)
- Salt (Rock Salt, Brines, Marine Salt)
- Sulfur (elementar and industrial Sulfur)
- Talc, Steatite and Pyrophyllite
- Vermiculite
- Zircon (concentrate)

#### Mineral Fuels:

- Steam Coal (incl. Anthracite, bituminous and sub-bituminous Coal)
- Coking Coal
- Lignite
- Natural Gas (marketed production) in million m3
- Oil Sands (gross production)
- Oil Shales
- Petroleum (incl. Natural Gas Liquids) (gross production)
- Uranium (U3O8)

### Contact
For any inquiries or feedback, please contact Ryan McKay on LinkedIn (/in/rdmckay) or at rmckayd [at] outlook [dot] com.
