# ruff: noqa: E501
from django.db import transaction

from ..models import Dish

dishes = [
    {
        "name": "Garden Fresh Salad",
        "description": "Crunchy mix of lettuce, tomatoes, cucumbers, and carrots with olive oil dressing",
        "ingredients": ["lettuce", "tomato", "cucumber", "carrot", "olive oil"],
    },
    {
        "name": "Roasted Seasonal Veggies",
        "description": "Assorted seasonal vegetables roasted with garlic and herbs",
        "ingredients": ["seasonal vegetables", "garlic", "herbs"],
    },
    {
        "name": "Veggie Burger",
        "description": "Plant-based patty with lettuce, tomato, and vegan mayo in a whole grain bun",
        "ingredients": ["plant-based patty", "lettuce", "tomato", "vegan mayo", "bun"],
    },
    {
        "name": "Creamy Tomato Soup",
        "description": "Smooth tomato soup with a hint of basil, served with croutons",
        "ingredients": ["tomato", "basil", "croutons", "dairy"],
    },
    {
        "name": "Quinoa Salad",
        "description": "Quinoa mixed with bell peppers, corn, and lime vinaigrette",
        "ingredients": ["quinoa", "bell pepper", "corn", "lime"],
    },
    {
        "name": "Stuffed Roasted Eggplant",
        "description": "Eggplant rolls filled with ricotta and spinach, baked to perfection",
        "ingredients": ["eggplant", "ricotta", "spinach", "dairy"],
    },
    {
        "name": "Mushroom Pasta",
        "description": "Pasta tossed with sautéed mushrooms, garlic, and parmesan",
        "ingredients": ["pasta", "mushroom", "garlic", "parmesan", "dairy"],
    },
    {
        "name": "Vegetarian Pizza",
        "description": "Thin crust pizza topped with mushrooms, onions, bell peppers, and mozzarella",
        "ingredients": [
            "pizza",
            "mushroom",
            "onion",
            "bell pepper",
            "mozzarella",
            "dairy",
        ],
    },
    {
        "name": "Butternut Squash Soup",
        "description": "Creamy soup made with butternut squash and spices",
        "ingredients": ["butternut squash", "spices", "dairy"],
    },
    {
        "name": "Chickpea Curry",
        "description": "Spiced chickpeas in a coconut milk sauce, served with rice",
        "ingredients": ["chickpea", "coconut milk", "rice"],
    },
    {
        "name": "Grilled Tofu Salad",
        "description": "Grilled tofu over mixed greens with avocado and balsamic dressing",
        "ingredients": ["tofu", "mixed greens", "avocado", "balsamic"],
    },
    {
        "name": "Spinach Lasagna",
        "description": "Layers of pasta, spinach, ricotta, and marinara sauce",
        "ingredients": ["pasta", "spinach", "ricotta", "marinara", "dairy"],
    },
    {
        "name": "Roasted Sweet Potatoes",
        "description": "Sweet potatoes roasted with cinnamon and a drizzle of honey",
        "ingredients": ["sweet potato", "cinnamon", "honey"],
    },
    {
        "name": "Vegetable Fried Rice",
        "description": "Rice stir-fried with carrots, peas, corn, and soy sauce",
        "ingredients": ["rice", "carrot", "peas", "corn", "soy sauce"],
    },
    {
        "name": "Lentil Soup",
        "description": "Hearty soup with lentils, carrots, and celery",
        "ingredients": ["lentil", "carrot", "celery"],
    },
    {
        "name": "Avocado Toast",
        "description": "Mashed avocado on sourdough bread with a sprinkle of red pepper flakes",
        "ingredients": ["bread", "avocado", "red pepper flakes"],
    },
    {
        "name": "Vegetable Spring Rolls",
        "description": "Crispy rolls filled with cabbage, carrots, and glass noodles",
        "ingredients": ["cabbage", "carrot", "glass noodles"],
    },
    {
        "name": "Broccoli with Cheese",
        "description": "Steamed broccoli topped with melted cheddar cheese",
        "ingredients": ["broccoli", "cheddar", "dairy"],
    },
    {
        "name": "Fresh Fruit Salad",
        "description": "Mix of seasonal fruits with a honey-yogurt dressing",
        "ingredients": ["fruit", "yogurt", "honey", "dairy"],
    },
    {
        "name": "Stir-Fried Tofu",
        "description": "Tofu stir-fried with broccoli, bell peppers, and ginger sauce",
        "ingredients": ["tofu", "broccoli", "bell pepper", "ginger sauce"],
    },
    {
        "name": "Grilled Ribeye Steak",
        "description": "Juicy ribeye steak seasoned with salt and pepper, grilled to your liking",
        "ingredients": ["beef"],
    },
    {
        "name": "Crispy Fried Chicken",
        "description": "Buttermilk-marinated chicken fried to golden perfection",
        "ingredients": ["chicken", "buttermilk", "dairy"],
    },
    {
        "name": "Pan-Seared Salmon",
        "description": "Fresh salmon fillet seared with lemon and dill",
        "ingredients": ["salmon", "fish"],
    },
    {
        "name": "Classic Cheeseburger",
        "description": "Beef patty with cheddar cheese, lettuce, tomato, and ketchup in a sesame bun",
        "ingredients": ["beef", "cheddar", "dairy", "bun"],
    },
    {
        "name": "Roast Chicken",
        "description": "Whole chicken roasted with herbs and garlic, served with gravy",
        "ingredients": ["chicken"],
    },
    {
        "name": "Pork Chop",
        "description": "Thick pork chop fried with apples and cinnamon",
        "ingredients": ["pork", "apple", "cinnamon"],
    },
    {
        "name": "Spaghetti with Italian Sausage",
        "description": "Spaghetti tossed with spicy Italian sausage and marinara",
        "ingredients": ["pork", "sausage", "pasta"],
    },
    {
        "name": "Shrimp Fried Rice",
        "description": "Rice stir-fried with shrimp, eggs, peas, and soy sauce",
        "ingredients": ["shrimp", "egg", "rice", "seafood"],
    },
    {
        "name": "Lamb Curry",
        "description": "Tender lamb pieces in a spicy curry sauce, served with rice",
        "ingredients": ["lamb", "rice", "spices"],
    },
    {
        "name": "Roast Beef",
        "description": "Slow-roasted beef with au jus and horseradish sauce",
        "ingredients": ["beef"],
    },
    {
        "name": "Turkey Sandwich",
        "description": "Sliced turkey with lettuce, tomato, and mayo on whole wheat bread",
        "ingredients": ["turkey", "lettuce", "tomato", "mayo", "egg"],
    },
    {
        "name": "Fish and Chips",
        "description": "Battered cod fillets with crispy french fries and tartar sauce",
        "ingredients": ["fish", "potato"],
    },
    {
        "name": "Pasta Carbonara",
        "description": "Pasta with eggs, pancetta, parmesan, and black pepper",
        "ingredients": ["pasta", "egg", "pancetta", "pork", "parmesan", "dairy"],
    },
    {
        "name": "Grilled Shrimp Skewers",
        "description": "Shrimp marinated in garlic and lemon, grilled on skewers",
        "ingredients": ["shrimp", "seafood", "garlic", "lemon"],
    },
    {
        "name": "Beef Tacos",
        "description": "Seasoned ground beef in corn tortillas with salsa and cheese",
        "ingredients": ["beef", "corn tortilla", "salsa", "cheese", "dairy"],
    },
    {
        "name": "Roast Duck",
        "description": "Duck roasted with orange glaze, served with roasted vegetables",
        "ingredients": ["duck"],
    },
    {
        "name": "Pepperoni Pizza",
        "description": "Thin crust pizza topped with pepperoni and mozzarella",
        "ingredients": ["pepperoni", "pork", "mozzarella", "dairy", "pizza"],
    },
    {
        "name": "Bacon Cheeseburger",
        "description": "Beef patty with bacon, cheddar, and BBQ sauce",
        "ingredients": ["beef", "bacon", "pork", "cheddar", "dairy", "bun"],
    },
    {
        "name": "Vegetable Omelette",
        "description": "Eggs folded with spinach, mushrooms, and cheese",
        "ingredients": ["egg", "spinach", "mushroom", "cheese", "dairy"],
    },
    {
        "name": "Barbecue Ribs",
        "description": "Pork ribs slow-cooked in BBQ sauce, fall-off-the-bone tender",
        "ingredients": ["pork", "ribs"],
    },
    {
        "name": "Tuna Salad",
        "description": "Canned tuna mixed with mayo, celery, and onions, served on lettuce",
        "ingredients": ["tuna", "fish", "mayo", "egg", "celery", "onion"],
    },
    {
        "name": "Chicken Caesar Salad",
        "description": "Grilled chicken over romaine lettuce with Caesar dressing and croutons",
        "ingredients": [
            "chicken",
            "romaine",
            "Caesar dressing",
            "anchovy",
            "fish",
            "parmesan",
            "dairy",
            "croutons",
        ],
    },
    {
        "name": "Lobster Pasta",
        "description": "Pasta with chunks of lobster in a creamy sauce",
        "ingredients": ["lobster", "seafood", "pasta", "cream", "dairy"],
    },
    {
        "name": "Sausage Rolls",
        "description": "Puff pastry wrapped around seasoned sausage meat, baked until golden",
        "ingredients": ["sausage", "pork", "pastry"],
    },
    {
        "name": "Buffalo Wings",
        "description": "Chicken wings coated in spicy buffalo sauce, served with ranch",
        "ingredients": ["chicken", "ranch", "dairy"],
    },
    {
        "name": "Beef Stew",
        "description": "Tender beef chunks with carrots, potatoes, and onions in a rich broth",
        "ingredients": ["beef", "carrot", "potato", "onion"],
    },
    {
        "name": "Ham and Egg Muffin",
        "description": "Ham and fried egg on an English muffin with cheese",
        "ingredients": ["ham", "pork", "egg", "cheese", "dairy", "muffin"],
    },
    {
        "name": "Salmon Salad",
        "description": "Smoked salmon with mixed greens, capers, and dill dressing",
        "ingredients": ["salmon", "fish", "greens", "capers", "dill"],
    },
    {
        "name": "Chicken Fried Rice",
        "description": "Rice stir-fried with chicken, eggs, and vegetables",
        "ingredients": ["chicken", "egg", "rice", "vegetables"],
    },
    {
        "name": "Grilled Lamb Chops",
        "description": "Lamb chops seasoned with rosemary and garlic, grilled to medium-rare",
        "ingredients": ["lamb", "garlic", "rosemary"],
    },
]


def run(*args):
    create_dishes = []
    for dish in dishes:
        create_dishes.append(
            Dish(
                name=dish["name"],
                description=dish["description"],
                ingredients=dish["ingredients"],
            )
        )
    with transaction.atomic():
        Dish.objects.all().delete()
        Dish.objects.bulk_create(create_dishes)
    print("Dishes data initialized successfully.")
