import django_filters

from .models import Opportunity


class OpportunityFilter(django_filters.FilterSet):
    type = django_filters.ChoiceFilter(field_name='opportunity_type', choices=Opportunity.OpportunityType.choices)
    experience_level = django_filters.ChoiceFilter(choices=Opportunity.ExperienceLevel.choices)
    education_level = django_filters.ChoiceFilter(choices=Opportunity.EducationLevel.choices)
    contract_type = django_filters.ChoiceFilter(choices=Opportunity.ContractType.choices)

    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    is_remote = django_filters.BooleanFilter(field_name='is_remote')

    category = django_filters.NumberFilter(field_name='category_id')
    skills = django_filters.BaseInFilter(field_name='skills__id', lookup_expr='in')

    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')

    class Meta:
        model = Opportunity
        fields = [
            'type', 'experience_level', 'education_level', 'contract_type',
            'city', 'country', 'is_remote', 'category', 'skills', 'salary_min',
        ]