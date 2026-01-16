"""
📊 VUES SQL OPTIMISÉES
Requêtes pré-calculées pour performance maximale
"""

def create_optimized_views(db):
    """
    Crée des vues SQL optimisées pour les requêtes fréquentes
    
    Args:
        db: Instance TurfDatabase
    """
    
    views = []
    
    # ==================== VUE : COURSES COMPLÈTES ====================
    
    views.append("""
        CREATE VIEW IF NOT EXISTS v_courses_complete AS
        SELECT 
            c.id as course_id,
            c.course_code,
            c.numero_course,
            c.heure,
            c.discipline,
            c.distance,
            c.allocation,
            c.nombre_partants,
            r.date as date_reunion,
            r.reunion_code,
            h.id as hippodrome_id,
            h.nom as hippodrome,
            h.pays
        FROM courses c
        JOIN reunions r ON c.reunion_id = r.id
        JOIN hippodromes h ON r.hippodrome_id = h.id
    """)
    
    # ==================== VUE : PARTANTS ENRICHIS ====================
    
    views.append("""
        CREATE VIEW IF NOT EXISTS v_partants_enrichis AS
        SELECT 
            p.id as partant_id,
            p.numero,
            p.cote_pmu,
            p.cote_bzh,
            p.rang_arrivee,
            
            c.course_code,
            c.discipline,
            c.distance,
            r.date as date_reunion,
            h.nom as hippodrome,
            
            ch.id as cheval_id,
            ch.nom as cheval_nom,
            ch.age as cheval_age,
            ch.sexe as cheval_sexe,
            ch.elo as cheval_elo,
            
            d.id as driver_id,
            d.nom as driver_nom,
            d.elo as driver_elo,
            d.taux_victoire as driver_taux_victoire,
            
            e.id as entraineur_id,
            e.nom as entraineur_nom,
            e.elo as entraineur_elo,
            
            p.ia_gagnant,
            p.ia_couple,
            p.ia_trio,
            p.note_ia,
            p.turf_points,
            p.tpch_90,
            p.tpj_365
            
        FROM partants p
        JOIN courses c ON p.course_id = c.id
        JOIN reunions r ON c.reunion_id = r.id
        JOIN hippodromes h ON r.hippodrome_id = h.id
        JOIN chevaux ch ON p.cheval_id = ch.id
        LEFT JOIN drivers d ON p.driver_id = d.id
        LEFT JOIN entraineurs e ON p.entraineur_id = e.id
        WHERE p.non_partant = 0
    """)
    
    # ==================== VUE : PERFORMANCES CHEVAUX ====================
    
    views.append("""
        CREATE VIEW IF NOT EXISTS v_perf_chevaux AS
        SELECT 
            ch.id as cheval_id,
            ch.nom as cheval,
            ch.elo,
            ch.nb_courses,
            ch.nb_victoires,
            ch.nb_places,
            ch.gains_total,
            ROUND(ch.nb_victoires * 100.0 / NULLIF(ch.nb_courses, 0), 2) as taux_victoire,
            ROUND(ch.nb_places * 100.0 / NULLIF(ch.nb_courses, 0), 2) as taux_place,
            ROUND(ch.gains_total / NULLIF(ch.nb_courses, 0), 0) as gain_moyen_course
        FROM chevaux ch
        WHERE ch.nb_courses > 0
    """)
    
    # ==================== VUE : PERFORMANCES DRIVERS ====================
    
    views.append("""
        CREATE VIEW IF NOT EXISTS v_perf_drivers AS
        SELECT 
            d.id as driver_id,
            d.nom as driver,
            d.elo,
            d.nb_courses,
            d.nb_victoires,
            d.taux_victoire,
            d.taux_place,
            ROUND(d.nb_victoires * 100.0 / NULLIF(d.nb_courses, 0), 2) as taux_victoire_calcule
        FROM drivers d
        WHERE d.nb_courses > 0
    """)
    
    # ==================== VUE : ROI PARIS ====================
    
    views.append("""
        CREATE VIEW IF NOT EXISTS v_roi_statistiques AS
        SELECT 
            p.type_pari,
            COUNT(*) as nb_paris,
            SUM(p.cout_total) as total_mise,
            SUM(p.gains) as total_gains,
            AVG(p.roi) as roi_moyen,
            SUM(CASE WHEN p.resultat = 'gagnant' THEN 1 ELSE 0 END) as nb_gagnants,
            ROUND(SUM(CASE WHEN p.resultat = 'gagnant' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as taux_reussite,
            MIN(p.roi) as roi_min,
            MAX(p.roi) as roi_max
        FROM paris p
        WHERE p.statut = 'termine'
        GROUP BY p.type_pari
    """)
    
    # ==================== VUE : HISTORIQUE RÉCENT ====================
    
    views.append("""
        CREATE VIEW IF NOT EXISTS v_historique_recent AS
        SELECT 
            p.partant_id,
            p.cheval_nom,
            p.driver_nom,
            p.course_code,
            p.hippodrome,
            p.date_reunion,
            p.numero,
            p.cote_pmu,
            p.rang_arrivee,
            CASE 
                WHEN p.rang_arrivee = 1 THEN '🥇 Victoire'
                WHEN p.rang_arrivee = 2 THEN '🥈 2ème'
                WHEN p.rang_arrivee = 3 THEN '🥉 3ème'
                WHEN p.rang_arrivee <= 5 THEN '✅ Top 5'
                ELSE '❌ Hors top 5'
            END as resultat_label
        FROM v_partants_enrichis p
        WHERE p.rang_arrivee IS NOT NULL
        ORDER BY p.date_reunion DESC
    """)
    
    # ==================== VUE : TOP CHEVAUX PAR HIPPODROME ====================
    
    views.append("""
        CREATE VIEW IF NOT EXISTS v_top_chevaux_hippodrome AS
        SELECT 
            h.nom as hippodrome,
            ch.nom as cheval,
            COUNT(*) as nb_courses,
            SUM(CASE WHEN p.rang_arrivee = 1 THEN 1 ELSE 0 END) as victoires,
            AVG(p.cote_pmu) as cote_moyenne,
            ROUND(SUM(CASE WHEN p.rang_arrivee = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as taux_victoire
        FROM partants p
        JOIN courses c ON p.course_id = c.id
        JOIN reunions r ON c.reunion_id = r.id
        JOIN hippodromes h ON r.hippodrome_id = h.id
        JOIN chevaux ch ON p.cheval_id = ch.id
        WHERE p.rang_arrivee IS NOT NULL
        GROUP BY h.id, ch.id
        HAVING nb_courses >= 3
    """)
    
    # ==================== VUE : SYNERGIES CHEVAL/DRIVER ====================
    
    views.append("""
        CREATE VIEW IF NOT EXISTS v_synergies_cheval_driver AS
        SELECT 
            ch.nom as cheval,
            d.nom as driver,
            COUNT(*) as nb_courses,
            SUM(CASE WHEN p.rang_arrivee = 1 THEN 1 ELSE 0 END) as victoires,
            SUM(CASE WHEN p.rang_arrivee <= 3 THEN 1 ELSE 0 END) as places,
            ROUND(SUM(CASE WHEN p.rang_arrivee = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as taux_victoire,
            ROUND(SUM(CASE WHEN p.rang_arrivee <= 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as taux_place,
            AVG(p.cote_pmu) as cote_moyenne
        FROM partants p
        JOIN chevaux ch ON p.cheval_id = ch.id
        JOIN drivers d ON p.driver_id = d.id
        WHERE p.rang_arrivee IS NOT NULL
        GROUP BY ch.id, d.id
        HAVING nb_courses >= 2
    """)
    
    # ==================== VUE : STATS PAR HIPPODROME ====================
    
    views.append("""
        CREATE VIEW IF NOT EXISTS v_stats_hippodromes AS
        SELECT 
            h.nom as hippodrome,
            COUNT(DISTINCT r.id) as nb_reunions,
            COUNT(DISTINCT c.id) as nb_courses,
            COUNT(p.id) as nb_partants,
            SUM(c.allocation) as allocation_totale,
            AVG(c.nombre_partants) as partants_moyen,
            MIN(r.date) as premiere_course,
            MAX(r.date) as derniere_course
        FROM hippodromes h
        LEFT JOIN reunions r ON h.id = r.hippodrome_id
        LEFT JOIN courses c ON r.id = c.reunion_id
        LEFT JOIN partants p ON c.id = p.course_id
        GROUP BY h.id
    """)
    
    # Créer toutes les vues
    for view_sql in views:
        try:
            db.cursor.execute(view_sql)
            print(f"✅ Vue créée")
        except Exception as e:
            print(f"⚠️ Erreur création vue: {e}")
    
    db.conn.commit()
    print(f"\n✅ {len(views)} vues SQL créées!")


def create_performance_indexes(db):
    """
    Crée des index supplémentaires pour optimiser les performances
    """
    
    indexes = [
        # Index composites pour requêtes fréquentes
        "CREATE INDEX IF NOT EXISTS idx_partants_course_numero ON partants(course_id, numero)",
        "CREATE INDEX IF NOT EXISTS idx_partants_cheval_date ON partants(cheval_id, course_id)",
        "CREATE INDEX IF NOT EXISTS idx_courses_date_hippodrome ON courses(reunion_id, discipline)",
        "CREATE INDEX IF NOT EXISTS idx_reunions_date_hippodrome ON reunions(date, hippodrome_id)",
        
        # Index pour les recherches textuelles
        "CREATE INDEX IF NOT EXISTS idx_chevaux_nom_lower ON chevaux(LOWER(nom))",
        "CREATE INDEX IF NOT EXISTS idx_drivers_nom_lower ON drivers(LOWER(nom))",
        
        # Index pour les tris
        "CREATE INDEX IF NOT EXISTS idx_chevaux_elo_desc ON chevaux(elo DESC)",
        "CREATE INDEX IF NOT EXISTS idx_drivers_elo_desc ON drivers(elo DESC)",
        
        # Index pour les statistiques
        "CREATE INDEX IF NOT EXISTS idx_paris_statut_type ON paris(statut, type_pari)",
        "CREATE INDEX IF NOT EXISTS idx_borda_scores_config ON borda_scores(config_id, score_total DESC)",
    ]
    
    for index_sql in indexes:
        try:
            db.cursor.execute(index_sql)
        except:
            pass
    
    db.conn.commit()
    print(f"✅ Index de performance créés!")


if __name__ == "__main__":
    from turf_database_complete import get_turf_database
    
    print("🔧 Création des vues SQL optimisées...")
    db = get_turf_database()
    
    create_optimized_views(db)
    create_performance_indexes(db)
    
    print("\n✅ Optimisation terminée!")
