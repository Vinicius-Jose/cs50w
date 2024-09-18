from django import forms

from .models import Bid, Commentary, Listing, User


def ajust_form_classes(visible_fields: list[forms.BoundField]):
    for visible in visible_fields:
        visible.field.widget.attrs["class"] = "form-control col-sm-10 "
        if isinstance(visible.field, forms.CheckboxInput):
            visible.field.widget.attrs["class"] = "custom-select my-1 mr-sm-2"
        elif isinstance(visible.field, forms.BooleanField):
            visible.field.widget.attrs["class"] = (
                "col-sm-2 form-check-input align-bottom"
            )
        elif isinstance(visible.field, forms.FloatField):
            visible.field.widget.attrs["class"] = " form-control col-sm-2"


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "category",
            "photo",
            "starting_bid",
            "is_active",
            "seller",
        ]

    def __init__(self, seller: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["seller"].initial = seller.id
        self.fields["seller"].disabled = True
        self.fields["seller"].widget = forms.HiddenInput()
        ajust_form_classes(self.visible_fields())


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["value", "user", "listing"]

    def __init__(self, user: User, listing: Listing, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].initial = user.id
        self.fields["user"].widget = forms.HiddenInput()
        self.fields["user"].disabled = True
        self.fields["listing"].initial = listing.id
        self.fields["listing"].widget = forms.HiddenInput()
        self.fields["listing"].disabled = True
        price = listing.get_current_price()
        self.fields["value"].widget.attrs["min"] = (
            price + 0.01
            if len(listing.listing_bids.all()) > 0
            else listing.starting_bid
        )
        ajust_form_classes(self.visible_fields())


class CommentaryForm(forms.ModelForm):
    class Meta:
        model = Commentary
        fields = ["text", "user", "listing"]

    def __init__(self, user: User, listing: Listing, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].initial = user.id
        self.fields["user"].widget = forms.HiddenInput()
        self.fields["user"].disabled = True
        self.fields["listing"].disabled = True
        self.fields["listing"].initial = listing.id
        self.fields["listing"].widget = forms.HiddenInput()
        ajust_form_classes(self.visible_fields())
