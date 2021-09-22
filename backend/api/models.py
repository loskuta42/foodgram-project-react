from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=254, blank=False)
    measurement_unit = models.CharField(max_length=20, blank=False)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=254,
        unique=True,
        blank=False
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff",
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        max_length=254,
        unique=True,
        blank=False
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
        blank=False,
        help_text='Введите название рецепта'
    )
    text = models.TextField(
        'Описание рецепта',
        blank=False,
        help_text='Введите описание рецепта'
    )
    image = models.ImageField(upload_to='recipes/', blank=False)
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                'Минимальное значение времени приготовления в минутах'
            )
        ],
        blank=False,
        default=1
    )
    tags = models.ManyToManyField(Tag, related_name='tags')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='ingredients'
    )
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        blank=False
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1, 'Минимальное значение')],
        blank=False
    )

    def __str__(self):
        return f'{self.ingredient} -> {self.recipe}'


class Favorite(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner_of_fav'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='fav_recipes'
    )

    class Meta:
        UniqueConstraint(
            fields=('owner', 'recipe'),
            name='unique_favourites'
        )


class Cart(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner_of_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop_recipes'
    )
