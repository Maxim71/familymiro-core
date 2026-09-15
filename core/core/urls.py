from django.contrib import admin
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap

# ==============================================================================
# ИМПОРТ ВСЕХ БОЕВЫХ И АВТОНОМНЫХ ФУНКЦИЙ ЭКОСИСТЕМЫ FAMILYMIRO
# ==============================================================================
from storage_control.views import (
    index_family,
    index_construction,
    qr_one_click_login,
    father_capital_vault,
    ezhik_kolokolchik_procurement,
    ai_video_optimizer,
    create_real_lava_invoice,
    real_lava_webhook,
    qr_pulsar_endpoint,
    central_monolith_architect_vault_gateway,
    ezhik_karma_boost_ribbon,
    generate_miro_secure_pdf_act,
    ezhik_find_goodness_parser,
    neuro_concrete_laboratory_radar,
    lava_api_payment_webhook,
    download_apk_gateway,
    fast_media_processor,
    trigger_ezhik_cicd_pipeline,
    portable_flash_drive_runner,
    generate_rk_specification_pdf,
    smart_input_transformer_gateway,
    dxf_blueprint_dashboard,
    ezhik_partner_diplomacy_gateway,
    architect_cocktail_lounge,
    global_adaptive_login,
    export_builders_cache_pdf,
    
    # Инфраструктурные, асинхронные и защитные утилиты Слоя 0.0
    global_country_transformer_gateway,
    ezhik_anarchic_intelligence_core,
    generate_miro_industrial_rfi,
    father_global_pulsar_dashboard,
    async_cyber_mutator_sentinel_task,
    check_mirror_zero_six_timeline,
    async_cyber_mutator
)
from storage_control.models import Agreement

# Автоматическая SEO-карта сайта для поисковиков Яндекса/Google
class AgreementSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    def items(self):
        return Agreement.objects.all()
    def location(self, item):
        return f"/capsule/{item.seo_slug}/"

# ==============================================================================
# ГЛОБАЛЬНЫЙ МАРШРУТИЗАТОР ВСЕЙ ЭКОСИСТЕМЫ FAMILYMIRO [1.6]
# ==============================================================================
from storage_control import views

# Эмуляция временных заглушек для предотвращения ошибок ImportError
def temporary_stub_view(request, *args, **kwargs):
    from django.http import JsonResponse
    return JsonResponse({"status": "PENDING", "message": "Контур ожидает физического подключения кода Архитектора."})

# Безопасное связывание недостающих в коде функций (Защитный щит от падения)
index_director = getattr(views, 'index_director', temporary_stub_view)
show_products_catalog = getattr(views, 'show_products_catalog', temporary_stub_view)
father_panel_view = getattr(views, 'father_panel_view', temporary_stub_view)
moderate_item = getattr(views, 'moderate_item', temporary_stub_view)
generate_messenger_share_link = getattr(views, 'generate_messenger_share_link', temporary_stub_view)
verify_face = getattr(views, 'verify_face', temporary_stub_view)
verify_qr_user_access = getattr(views, 'verify_qr_user_access', temporary_stub_view)
procurement_approval_flow = getattr(views, 'procurement_approval_flow', temporary_stub_view)
get_snip_and_fire_safety = getattr(views, 'get_snip_and_fire_safety', temporary_stub_view)
upload_defect_photos = getattr(views, 'upload_defect_photos', temporary_stub_view)
generate_ks3 = getattr(views, 'generate_ks3', temporary_stub_view)


urlpatterns = [
    # 👑 Главная страница (Вековой Сейф / Храм Вечности) — АКТИВНА ✅
    path('', index_family, name='index_family'),
    
    # 🌌 Главная админ-панель управления Django
    path('admin/', admin.site.urls),
    
    # 🎬 Открытые пульты управления контурами (Гренландский минимализм)
    path('director/', index_director, name='index_director'),
    path('construction/', index_construction, name='index_construction'),  # АКТИВНА ✅
    path('products/', show_products_catalog, name='products_catalog'),
    path('father-panel/', father_panel_view, name='father_panel'),
    
    # 🦔 Модерация, шеринг и парсинг добра Ёжика
    path('api/moderate/<int:item_id>/', moderate_item, name='moderate_item'),
    path('api/ezhik/parse/', ezhik_find_goodness_parser, name='ezhik_parse'),  # АКТИВНА ✅
    path('api/ezhik/portable/', portable_flash_drive_runner, name='portable_drive_runner'),  # АКТИВНА ✅
    path('api/ezhik/submit-comment/', ezhik_karma_boost_ribbon, name='submit_comment'),  # АКТИВНА ✅
    path('api/share/link/', generate_messenger_share_link, name='messenger_share_link'),
    
    # 📲 Шлюзы авторизации, Kivy и верификации биометрии
    path('api/blogger/qr-login/', qr_one_click_login, name='blogger_qr_login'),  # АКТИВНА ✅
    path('api/verify-face/', verify_face, name='verify_face'),
    path('api/kivy/verify/', verify_qr_user_access, name='kivy_verify'),
    path('download/apk/', download_apk_gateway, name='download_apk_gateway'),  # АКТИВНА ✅
    
    # 👑 Личные скрытые сейфы Отца, ИИ-Колокольчик и конвейер DevOps CI/CD
    path('api/father/vault/', father_capital_vault, name='father_vault'),  # АКТИВНА ✅
    path('api/ezhik/procurement/', ezhik_kolokolchik_procurement, name='ezhik_procurement'),  # АКТИВНА ✅
    path('api/father/cicd/', trigger_ezhik_cicd_pipeline, name='trigger_ezhik_cicd'),  # АКТИВНА ✅

    # 👑 СЕКРЕТНЫЙ ШЛЮЗ АРХИТЕКТОРА (МАКСИМА):
    path('architect/', views.architect_cocktail_lounge, name='architect_lounge'),  # АКТИВНА ✅
    
    # 🏗️ ЕДИНЫЙ АДАПТИВНЫЙ ВХОД ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ И ГРУПП (СТРОИТЕЛЕЙ):
    path('portal-login/', views.global_adaptive_login, name='global_login'),  # АКТИВНА ✅
    
    # 🎬 Контур скорости и ИИ-монтаж видео для блогеров
    path('api/blogger/process-video/', ai_video_optimizer, name='blogger_process_video'),  # АКТИВНА ✅
    path('api/media/fast-process/', fast_media_processor, name='fast_media_processor'),  # АКТИВНА ✅
    
    # 💳 Контур Монетизации, Альфа-Банк ЭДО и шлюзы СБП LAVA
    path('api/revenue/buy-passport/', create_real_lava_invoice, name='buy_passport'),  # АКТИВНА ✅
    path('api/lava-webhook/', real_lava_webhook, name='lava_webhook'),  # АКТИВНА ✅
    path('api/lava-api/webhook/', lava_api_payment_webhook, name='lava_api_webhook'),  # АКТИВНА ✅
    path('api/qr-pulsar/', qr_pulsar_endpoint, name='qr_pulsar'),  # АКТИВНА ✅
    
    # 🏗️ ИИ-Технадзор, Радары Снабжения, СНиПы, Чертежи и Дефекты по ГОСТ
    path('api/construction/roof/', central_monolith_architect_vault_gateway, name='roof_control'),  # АКТИВНА ✅
    path('api/construction/procurement/', procurement_approval_flow, name='procurement_flow'),
    path('api/construction/regulations/', get_snip_and_fire_safety, name='get_regulations'),
    path('api/construction/upload-defect/', upload_defect_photos, name='upload_defect'),
    path('api/construction/radar/', neuro_concrete_laboratory_radar, name='neuro_radar'),  # АКТИВНА ✅
    path('api/construction/dxf-scan/', dxf_blueprint_dashboard, name='dxf_blueprint_scan'),  # АКТИВНА ✅
    path('api/construction/transformer/', smart_input_transformer_gateway, name='input_transformer'),  # АКТИВНА ✅

    # 📄 Автоматическая выгрузка исполнительных актов КС-2 / КС-3 / ReportLab PDF
    path('api/construction/generate-ks2/', generate_miro_secure_pdf_act, name='generate_ks2'),  # АКТИВНА ✅
    path('api/construction/generate-ks3/', generate_ks3, name='generate_ks3'),
    path('api/construction/concrete-pdf/', generate_rk_specification_pdf, name='generate_concrete_pdf'),  # АКТИВНА ✅
    
    # 🔍 Инфраструктурные SEO-сервисы поисковых роботов
    path('sitemap.xml', sitemap, {'sitemaps': {'agreements': AgreementSitemap}}, name='django.contrib.sitemaps.views.sitemap'),

    # SPLIT
    path('architect-lounge/', views.architect_cocktail_lounge, name='cocktail_lounge'),  # АКТИВНА ✅
    path('api/ezhik/diplomacy/', ezhik_partner_diplomacy_gateway, name='ezhik_diplomacy'),  # АКТИВНА ✅
]
