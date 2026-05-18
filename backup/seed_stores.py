import os
import django
import unicodedata

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_system.settings')
django.setup()

from django.db import connection

# ============================================================
# STEP 1: Buat tabel lumra_config_stores jika belum ada
# ============================================================
def create_stores_table():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'lumra_config_stores'
            );
        """)
        exists = cursor.fetchone()[0]

        if not exists:
            print("🔧 Membuat tabel lumra_config_stores...")
            cursor.execute("""
                CREATE TABLE lumra_config_stores (
                    id          BIGSERIAL PRIMARY KEY,
                    name        VARCHAR(100) NOT NULL UNIQUE,
                    subdomain   VARCHAR(100) NOT NULL UNIQUE,
                    business_type VARCHAR(20) NOT NULL 
                                  CHECK (business_type IN ('fnb', 'fashion', 'retail', 'beauty')),
                    description TEXT DEFAULT '',
                    logo_url    VARCHAR(255),
                    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
                    plan        VARCHAR(20) NOT NULL DEFAULT 'starter'
                                CHECK (plan IN ('starter', 'growth', 'enterprise')),
                    owner_id    INTEGER NOT NULL 
                                REFERENCES auth_user(id) ON DELETE RESTRICT,
                    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                -- Index untuk performa query SaaS multi-tenant
                CREATE INDEX idx_stores_owner     ON lumra_config_stores(owner_id);
                CREATE INDEX idx_stores_subdomain ON lumra_config_stores(subdomain);
                CREATE INDEX idx_stores_biz_type  ON lumra_config_stores(business_type);
                CREATE INDEX idx_stores_active    ON lumra_config_stores(is_active);

                -- Auto-update updated_at trigger
                CREATE OR REPLACE FUNCTION update_stores_updated_at()
                RETURNS TRIGGER AS $$
                BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER trg_stores_updated_at
                    BEFORE UPDATE ON lumra_config_stores
                    FOR EACH ROW EXECUTE FUNCTION update_stores_updated_at();
            """)
            print("✅ Tabel lumra_config_stores berhasil dibuat!")
        else:
            print("🟡 Tabel lumra_config_stores sudah ada, skip pembuatan.")

# ============================================================
# STEP 2: Seed data stores
# ============================================================
def make_slug(name):
    normalized = unicodedata.normalize('NFKD', name)
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
    return (ascii_name.lower()
            .replace(" ", "-")
            .replace("'", "")
            .replace(".", "")
            .replace("&", "and")
            .replace(",", "")
            .strip("-"))

def seed_lumra_stores():
    from django.contrib.auth.models import User

    owner = User.objects.filter(is_superuser=True).first()
    if not owner:
        owner = User.objects.first()
    if not owner:
        print("❌ Error: Belum ada User di database!")
        print("   Jalankan: python manage.py createsuperuser")
        return

    print(f"👤 Owner: {owner.username} (id={owner.id})")

    stores_data = [
        # COFFEE SHOPS (FnB)
        ("Veloce Brew", "fnb"),
        ("LEredita Coffee", "fnb"),
        ("Minimalist Bean", "fnb"),
        ("Aura Espresso Lab", "fnb"),
        ("Caffe Prototipo", "fnb"),
        ("Symmetry Roasters", "fnb"),
        ("Iconic Brew Co", "fnb"),
        ("Nero dAvola Coffee", "fnb"),
        ("Zenith Coffee House", "fnb"),
        ("Lumina Beans", "fnb"),
        # RESTAURANTS (FnB)
        ("Aeterna Bistro", "fnb"),
        ("Forma Kitchen", "fnb"),
        ("Elemento Grill", "fnb"),
        ("Prisma Dining", "fnb"),
        ("Vanguard Table", "fnb"),
        ("Essentia Gastronomy", "fnb"),
        # FASHION
        ("Moda Allegra", "fashion"),
        ("Stile Veloce", "fashion"),
        ("The Monolith Store", "fashion"),
        ("Canvas Co", "fashion"),
        ("Linear Boutique", "fashion"),
        ("Aesthetic Archive", "fashion"),
        ("Veritas Wear", "fashion"),
        ("Onyx Apparels", "fashion"),
        ("Nordic Thread", "fashion"),
        ("Aura Ready-to-Wear", "fashion"),
        ("Primal Luxe", "fashion"),
        ("Epoca Boutique", "fashion"),
        ("Volo Fashion", "fashion"),
        ("Grit and Silk", "fashion"),
        ("Lumina Style Hub", "fashion"),
        ("Structure Label", "fashion"),
        ("Cura Collection", "fashion"),
        ("Sphere Clothing", "fashion"),
        ("Minimal Threads", "fashion"),
        ("Iconic Attire", "fashion"),
    ]

    print(f"\n🚀 Memasukkan {len(stores_data)} Brand ke Database Lumra...")
    created_count = 0
    skipped_count = 0

    with connection.cursor() as cursor:
        for name, b_type in stores_data:
            slug = make_slug(name)

            # Cek apakah sudah ada
            cursor.execute(
                "SELECT id FROM lumra_config_stores WHERE name = %s", [name]
            )
            row = cursor.fetchone()

            if row:
                print(f"  🟡 Skipped : {name}")
                skipped_count += 1
            else:
                cursor.execute("""
                    INSERT INTO lumra_config_stores 
                        (name, subdomain, business_type, is_active, plan, owner_id, created_at, updated_at)
                    VALUES (%s, %s, %s, TRUE, 'starter', %s, NOW(), NOW())
                """, [name, slug, b_type, owner.id])
                print(f"  ✅ Created : {name:<30} → {slug}.lumra.id")
                created_count += 1

    print(f"\n{'='*55}")
    print(f"  ✨ Selesai! {created_count} dibuat, {skipped_count} dilewati.")
    print(f"{'='*55}")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    create_stores_table()
    seed_lumra_stores()