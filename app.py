from flask import Flask, request, render_template
from PIL import Image, ImageFilter
from pprint import PrettyPrinter
import json
import os
import random
import requests

app = Flask(__name__)

@app.route('/')
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template('home.html')

################################################################################
# COMPLIMENTS ROUTES
################################################################################

list_of_compliments = [
    'awesome',
    'beatific',
    'blithesome',
    'conscientious',
    'coruscant',
    'erudite',
    'exquisite',
    'fabulous',
    'fantastic',
    'gorgeous',
    'indubitable',
    'ineffable',
    'magnificent',
    'outstanding',
    'propitioius',
    'remarkable',
    'spectacular',
    'splendiferous',
    'stupendous',
    'super',
    'upbeat',
    'wondrous',
    'zoetic'
]

@app.route('/compliments')
def compliments():
    """Shows the user a form to get compliments."""
    return render_template('compliments_form.html')

@app.route('/compliments_results')
def compliments_results():
    """Show the user some compliments."""
    # Save keys and values from compliments_form.html
    context = {
        'users_name': request.args.get('users_name'),
        'wants_compliments': request.args.get('wants_compliments'),
        'num_compliments': int(request.args.get('num_compliments'))
    }
    # Append the dictionary with a random sample of compliments 
    # (dictionary name in k-parameter cannot be called before initialization)
    context['random_compliments'] = random.sample(list_of_compliments, k=context['num_compliments'])

    return render_template('compliments_results.html', **context)


################################################################################
# ANIMAL FACTS ROUTE
################################################################################

# Dictionary of animals as keys and interesting tidbits as values
animal_to_fact = {
    'koala': 'Koala fingerprints are so close to humans\' that they could taint crime scenes.',
    'parrot': 'Parrots will selflessly help each other out.',
    'mantis shrimp': 'The mantis shrimp has the world\'s fastest punch.',
    'lion': 'Female lions do 90 percent of the hunting.',
    'narwhal': 'Narwhal tusks are really an "inside out" tooth.',
    'puffin': 'Puffins use twigs to scratch their bodies.',
    'shark': 'Some sharks glow in the dark.',
    'grizzly bear': "A grizzly bear's bite is strong enough to crush a bowling ball.",
    'zebra': 'Zebra stripes act as a natural bug repellant.',
    'octopus': 'Octopuses can taste with their arms.',
    'reindeer': 'Reindeer eyes turn blue in the winter.'
}

@app.route('/animal_facts')
def animal_facts():
    """Show a form to choose an animal and receive facts."""

    # Save the user's choice of animal
    chosen_animal = request.args.get('animal')

    context = {
        # The list of all animals retrieved as keys from `animal_to_facts` dictionary
        'animals': animal_to_fact.keys(),
        # The chosen animal fact retrieved as a value from `animal_to_facts` dictionary via `get()`
        # (may be None if the user hasn't filled out the form yet)
        'animal_fact': animal_to_fact.get(chosen_animal)
    }
    return render_template('animal_facts.html', **context)


################################################################################
# IMAGE FILTER ROUTE
################################################################################

filter_types_dict = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR,
    'detail': ImageFilter.DETAIL,
    'edge enhance': ImageFilter.EDGE_ENHANCE,
    'edge enhance more': ImageFilter.EDGE_ENHANCE_MORE,
    'emboss': ImageFilter.EMBOSS,
    'find edges': ImageFilter.FIND_EDGES,
    'sharpen': ImageFilter.SHARPEN,
    'smooth': ImageFilter.SMOOTH,
    'smooth more': ImageFilter.SMOOTH_MORE
}

def save_image(image, filter_type):
    """Save the image, then return the full file path of the saved image."""
    # Append the filter type at the beginning (in case the user wants to 
    # apply multiple filters to 1 image, there won't be a name conflict)
    new_file_name = f"{filter_type}-{image.filename}"
    image.filename = new_file_name

    # Construct full file path
    file_path = os.path.join(app.root_path, 'static/images', new_file_name)
    
    # Save the image
    image.save(file_path)

    return file_path


def apply_filter(file_path, filter_name):
    """Apply a Pillow filter to a saved image."""
    i = Image.open(file_path)
    i.thumbnail((500, 500))
    i = i.filter(filter_types_dict.get(filter_name))
    i.save(file_path)

@app.route('/image_filter', methods=['GET', 'POST'])
def image_filter():
    """Filter an image uploaded by the user, using the Pillow library."""
    filter_types = filter_types_dict.keys()

    if request.method == 'POST':
        
        # Save the user's choice of filter type from the drop-down menu
        filter_type = request.form.get('filter_type')
        
        # Get the image file submitted by the user
        image = request.files.get('users_image')

        # Call `save_image()` on the image & the user's chosen filter type and save the returned
        # value as the new file path
        new_file_path = save_image(image, filter_type)

        # Call `apply_filter()` on the file path & filter type
        apply_filter(new_file_path, filter_type)

        # Save the filename to a full URL
        image_url = f'/static/images/{image.filename}'

        context = {
            # The full list of filter types
            'list_of_filter_types': filter_types,
            # The image URL
            'image_URL': image_url
        }

        return render_template('image_filter.html', **context)

    else: # if it's a GET request
        context = {
            # The full list of filter types
            'list_of_filter_types': filter_types_dict.keys(),
        }
        return render_template('image_filter.html', **context)


################################################################################
# GIF SEARCH ROUTE
################################################################################

API_KEY = 'LIVDSRZULELA'
TENOR_URL = 'https://api.tenor.com/v1/search'
pp = PrettyPrinter(indent=4)

@app.route('/gif_search', methods=['GET', 'POST'])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    if request.method == 'POST':
        # Save the search query from the user
        search_query = request.form.get('search_query')
        # Save the number of GIFs requested by the user
        quantity = request.form.get('quantity')

        response = requests.get(
            TENOR_URL,
            {
                # Add in key-value pairs for:
                # - 'q': the search query
                'q': search_query,
                # - 'key': the API key (defined above)
                'key': API_KEY,
                # - 'limit': the number of GIFs requested
                'limit': quantity
            })

        gifs = json.loads(response.content).get('results')

        context = {
            'gifs': gifs
        }

        # Uncomment me to see the result JSON!
        pp.pprint(gifs)

        return render_template('gif_search.html', **context)
    else:
        return render_template('gif_search.html')

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)