from django import forms

from aliss.models import Claim
from aliss.models import Claim, Organisation, ALISSUser

class ClaimForm(forms.Form):
    comment = forms.CharField(required=True,
        widget=forms.Textarea(), label="What is your role in the organisation?")
    phone = forms.CharField(
        required=True,
        help_text="The phone number we should use to verify you as the owner of this organisation")
    data_quality = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the data standards required on ALISS'},
        label="I understand and acknowledge the importance of data quality and agree to follow the guidance outlined in the ALISS Data Standards")

    class Meta:
        error_css_class = 'has-error'

class ClaimUpdateForm(forms.ModelForm):
    status = forms.ChoiceField(
                choices=(
                    (Claim.CONFIRMED, "Confirm Claim"),
                    (Claim.REVOKED, "Revoke Claim"),
                    (Claim.DENIED, "Deny Claim"),
                    (Claim.UNREVIEWED, "Review Claim"),
                ),
                widget=forms.RadioSelect()
             )

    class Meta:
        model = Claim
        fields = (
            'status',
        )
        error_css_class = 'has-error'
