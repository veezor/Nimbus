from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True, db_column='iduser')
    username = models.CharField(max_length=195)

    class Meta:
        db_table = u'users'


class Plan(models.Model):
    id = models.IntegerField(primary_key=True, db_column='idplano')
    size = models.BigIntegerField(db_column='espaco_bytes')

    class Meta:
        db_table = u'planos_nimbus'


class UserPlans(models.Model):
    user = models.ForeignKey(User,db_column='id_user')
    plan = models.ForeignKey(Plan, db_column='id_plano_nimbus')
    class Meta:
        db_table = u'users_planos_nimbus'
        unique_together = ('user', 'plan')



