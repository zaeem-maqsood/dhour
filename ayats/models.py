from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg


# Create your models here.
class Ayat(models.Model):
    surah = models.IntegerField()
    number = models.IntegerField()
    ayat_in_surah = models.IntegerField()

    def __str__(self):
        return f"{self.surah} : {self.ayat_in_surah}"

    class Meta:
        verbose_name = "Ayat"
        verbose_name_plural = "Ayat"


class UserAyatState(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ayat = models.ManyToManyField(Ayat)
    reviewed_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()
    weight = models.FloatField(default=1)

    def __str__(self):
        return f"{self.user}"

    class Meta:
        verbose_name = "User Ayat State"
        verbose_name_plural = "User Ayat States"

    # !! USED IN A SIGNAL !!
    # See dhour/ayats/signals.py
    # We need to update the overlapping user states when we save a new user state
    def update_overlapping_user_states(self):
        overlapping_user_states = UserAyatState.objects.filter(
            user=self.user, ayat__in=self.ayat.all()
        ).exclude(pk=self.pk)
        for user_state in overlapping_user_states:
            print("user_state", user_state.id)
            user_state.ayat.remove(*self.ayat.all())
            # If all the ayat are reviewed within other user states, delete this user state
            if user_state.ayat.count() == 0:
                user_state.delete()
            else:
                user_state.save()

    def calculate_user_ayat_state_weight(self):
        """
        This function calculates the weight for a UserAyatState based on the time
        between reviewed_date and review_expiration_date, and the default_expiry_time
        for the user.
        """

        # Get the reviewed date and the expiration date
        reviewed_date = self.reviewed_date
        expiration_date = self.expiration_date

        # Get the default expiry time from the associated user
        user = self.user
        default_expiry_time = user.default_expiry_time

        # Calculate the remaining time in days
        remaining_time = (expiration_date - reviewed_date).days

        # Calculate the weight: this represents the proportion of time elapsed
        weight = 1 - ((default_expiry_time - remaining_time) / default_expiry_time)

        # Ensure weight is between 0 and 1
        if weight < 0:
            weight = 0
        elif weight > 1:
            weight = 1

        return weight

    # Override the save method to update the weight before saving
    def save(self, *args, **kwargs):
        # Calculate the weight
        self.weight = self.calculate_user_ayat_state_weight()

        # Call the superclass save method to complete the save operation
        super().save(*args, **kwargs)


class UserHizbState(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    hizb = models.ForeignKey("HizbQuarter", on_delete=models.CASCADE)
    weight = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user} : {self.hizb}"

    class Meta:
        verbose_name = "Hizb User State"
        verbose_name_plural = "Hizb User States"
        indexes = [
            models.Index(fields=["user", "hizb"]),
        ]


def calculate_hizb_weight(user, hizb_quarter):
    # Get all the ayat associated with the given hizb_quarter
    ayat_in_hizb = hizb_quarter.ayat.all()

    # Get all UserAyatState objects for the specified user
    user_ayat_states = UserAyatState.objects.filter(user=user)

    # Find UserAyatState objects with overlapping ayat
    overlapping_user_ayat_states = user_ayat_states.filter(
        ayat__in=ayat_in_hizb
    ).distinct()

    # Aggregate the total weight of these UserAyatState objects
    aggregated_weight = overlapping_user_ayat_states.aggregate(
        total_weight=Avg("weight")
    )

    # Extract the total weight (or default to 0 if None)
    total_weight = aggregated_weight["total_weight"] or 0

    return total_weight


class UserJuzState(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    juz = models.ForeignKey("Juz", on_delete=models.CASCADE)
    weight = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user} : {self.juz}"

    class Meta:
        verbose_name = "Juz User State"
        verbose_name_plural = "Juz User States"
        indexes = [
            models.Index(fields=["user", "juz"]),
        ]


def calculate_juz_weight(user, juz):
    # Get all the hizb quarters associated with the given juz
    hizb_quarters_in_juz = juz.hizbquarter_set.all()

    # Get all UserHizbState objects for the specified user
    user_hizb_states = UserHizbState.objects.filter(user=user)

    # Find UserHizbState objects with overlapping hizb quarters
    user_hizb_states = user_hizb_states.filter(hizb__in=hizb_quarters_in_juz)

    # Aggregate the total weight of these UserHizbState objects
    aggregated_weight = user_hizb_states.aggregate(total_weight=Avg("weight"))

    # Extract the total weight (or default to 0 if None)
    total_weight = aggregated_weight["total_weight"] or 0

    return total_weight


class Section(models.Model):
    ayat = models.ManyToManyField(Ayat)

    class Meta:
        abstract = True


class Ruku(Section):
    number = models.IntegerField()

    def __str__(self):
        return f"{self.number}"

    class Meta:
        verbose_name = "Ruku"
        verbose_name_plural = "Ruku"


class HizbQuarter(Section):
    juz = models.ForeignKey("Juz", on_delete=models.CASCADE)
    number = models.IntegerField()

    def __str__(self):
        return f"Hizb: {self.number} | Juz: {self.juz} : "

    class Meta:
        verbose_name = "Hizb Quarter"
        verbose_name_plural = "Hizb Quarters"


class Juz(Section):
    number = models.IntegerField()

    def __str__(self):
        return f"{self.number}"

    class Meta:
        verbose_name = "Juz"
        verbose_name_plural = "Juz"
