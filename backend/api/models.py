from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=254,
        blank=False,
        verbose_name='Название ингредиента',
        help_text=('Введите название ингредиента,'
                   ' не более 254 символов')
    )
    measurement_unit = models.CharField(
        max_length=20,
        blank=False,
        verbose_name='Величина измерения',
        help_text=('Введите величину измерения,'
                   'не более 20 символов')
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Название тэга',
        help_text=('Введите название тэга, '
                   'не более 254 символов')
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff",
        unique=True,
        blank=False,
        verbose_name='Цвет тега',
        help_text=('Введите цвет тэга в формате HEX, '
                   'пример: #123adf')
    )
    slug = models.SlugField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Slug тега',
        help_text=('Введите slug тэга, '
                   'не более 254 символов')
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Укажите автора рецепта'
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название рецепта',
        help_text=('Введите название рецепта, '
                   'не более 200 символов')
    )
    text = models.TextField(
        blank=False,
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        verbose_name='Фото готового блюда',
        help_text=('Прикрепите фото блюда приготовленного '
                   'по приведенному рецепту')
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                1,
                'Минимальное значение времени приготовления в минутах'
            ),
        ),
        blank=False,
        default=1,
        verbose_name='Время приготовления',
        help_text='Введите время приготовления в минутах'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тэги',
        help_text=('Выберите тэги, которым будет '
                   'соответствовать рецепт')
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='ingredients',
        verbose_name='Игредиенты',
        help_text=('Выберите ингредиенты, которые '
                   'понадобятся в ходе приготовления '
                   'блюда по рецепту')
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации рецепта'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        blank=False,
        verbose_name='Ингредиент',
        help_text='Выберите ингредиент рецепта'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(MinValueValidator(1, 'Минимальное значение'),),
        blank=False,
        verbose_name='Количество ингредиента',
        help_text=('Введите количество ингредиента в рецепте,'
                   ' значение должно быть не более 1')
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.ingredient.name} -> {self.recipe.name}'


class Favorite(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner_of_fav',
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='fav_recipes',
        verbose_name='Изранный рецепт',
        help_text='Выберите изранный рецепт'
    )

    class Meta:
        constraints = (UniqueConstraint(
            fields=('owner', 'recipe'),
            name='unique_favourites'
        ),)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.owner.username} -> {self.recipe.name}'


class Cart(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner_of_cart',
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop_recipes',
        verbose_name='Рецепт в списке покупок',
        help_text=('Выберите рецепт для добавления в '
                   'список покупок в списке покупок')
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.owner.username} -> {self.recipe.name}'
