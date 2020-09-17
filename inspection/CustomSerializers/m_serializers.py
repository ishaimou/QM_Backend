from inspection.models import ProductCategory, ProductFamily, ProductType, Product
from rest_framework import serializers
from inspection.serializers import ProductFamilySerializer, ProductCategorySerializer, ProductTypeSerializer


class ProductListSerializer(serializers.ModelSerializer):
    
    category = serializers.SerializerMethodField('get_category')
    family = serializers.SerializerMethodField('get_family')
    type = serializers.SerializerMethodField('get_type')

    class Meta:
        model = Product
        fields = ('id', 'name', 'product_category_ref', 'category', 'family', 'type')

    def get_category(self, product):
        queryset = ProductCategory.objects.get(id=product.product_category_ref.id)
        serializer = ProductCategorySerializer(queryset)
        return serializer.data['name']

    def get_family(self, product):
        queryset = ProductFamily.objects.get(id=product.product_category_ref.product_family_ref.id)
        serializer = ProductFamilySerializer(queryset)
        return serializer.data['name']

    def get_type(self, product):
        queryset = ProductType.objects\
                    .get(id=product.product_category_ref.product_family_ref.product_type_ref.id)
        serializer = ProductTypeSerializer(queryset)
        return serializer.data['name']