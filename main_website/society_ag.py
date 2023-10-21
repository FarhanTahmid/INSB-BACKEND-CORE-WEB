from ieee_nsu_sb_ras_sbc.models import Ras_Sbc


class Ras:
    
    def get_ras_about():
        try:
            about_ras=Ras_Sbc.objects.all()
            return about_ras[0]
        except:
            return False
    