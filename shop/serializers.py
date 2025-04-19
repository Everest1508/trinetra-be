from rest_framework import serializers
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from users.models import UserProfile

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    is_parent = serializers.SerializerMethodField()
    is_child = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'parent_name',
                 'is_parent', 'is_child', 'subcategories', 'created_at']

    def get_subcategories(self, obj):
        serializer = CategorySerializer(obj.subcategories.all(), many=True)
        return serializer.data

    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None

    def get_is_parent(self, obj):
        return obj.is_parent

    def get_is_child(self, obj):
        return obj.is_child

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'stock', 
                 'image', 'is_available', 'category', 'category_id']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'created_at']

    def get_total(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.none(),  # This will be set in the view
        required=True
    )

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'shipping_address', 
                 'created_at', 'items']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'request' in self.context:
            self.fields['shipping_address'].queryset = self.context['request'].user.addresses.all()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'city', 'state', 
                 'country', 'postal_code'] 