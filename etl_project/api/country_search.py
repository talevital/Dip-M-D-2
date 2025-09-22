"""
Module de recherche de pays via l'API Nominatim d'OpenStreetMap
"""

from fastapi import APIRouter, Query, HTTPException
import httpx
import logging

logger = logging.getLogger(__name__)

# Créer un router pour les endpoints de recherche de pays
router = APIRouter(prefix="/search", tags=["country-search"])

@router.get("/country")
async def search_country(q: str = Query(..., description="Code ou nom du pays")):
    """
    Recherche un pays par son nom ou code via l'API Nominatim d'OpenStreetMap
    
    Args:
        q: Code ou nom du pays à rechercher
        
    Returns:
        dict: Informations géographiques du pays trouvé
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "format": "json",
            "q": q,
            "limit": 1,
            "type": "country",
            "polygon_geojson": 1,
        }
        headers = {
            "User-Agent": "DIP-Project/1.0 (contact@dip-project.com)",
            "Accept-Language": "fr",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Aucun pays trouvé pour la recherche: {q}"
                )
            
            # Retourner le premier résultat
            country_data = data[0]
            
            logger.info(f"Country search successful for: {q}")
            
            return {
                "success": True,
                "query": q,
                "country": {
                    "name": country_data.get("display_name", ""),
                    "place_id": country_data.get("place_id"),
                    "lat": country_data.get("lat"),
                    "lon": country_data.get("lon"),
                    "boundingbox": country_data.get("boundingbox"),
                    "geojson": country_data.get("geojson"),
                    "importance": country_data.get("importance"),
                    "osm_type": country_data.get("osm_type"),
                    "osm_id": country_data.get("osm_id")
                }
            }
            
    except httpx.TimeoutException:
        logger.error(f"Timeout lors de la recherche du pays: {q}")
        raise HTTPException(
            status_code=408, 
            detail="Timeout lors de la recherche. Veuillez réessayer."
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Erreur HTTP lors de la recherche du pays {q}: {e}")
        raise HTTPException(
            status_code=502, 
            detail="Erreur lors de la communication avec le service de géolocalisation"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la recherche du pays {q}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur interne du serveur: {str(e)}"
        )

@router.get("/countries")
async def search_countries(
    q: str = Query(..., description="Terme de recherche pour les pays"),
    limit: int = Query(5, description="Nombre maximum de résultats", ge=1, le=20)
):
    """
    Recherche multiple pays par terme de recherche
    
    Args:
        q: Terme de recherche
        limit: Nombre maximum de résultats (1-20)
        
    Returns:
        dict: Liste des pays trouvés
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "format": "json",
            "q": q,
            "limit": limit,
            "type": "country",
            "polygon_geojson": 1,
        }
        headers = {
            "User-Agent": "DIP-Project/1.0 (contact@dip-project.com)",
            "Accept-Language": "fr",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Aucun pays trouvé pour la recherche: {q}"
                )
            
            countries = []
            for country_data in data:
                countries.append({
                    "name": country_data.get("display_name", ""),
                    "place_id": country_data.get("place_id"),
                    "lat": country_data.get("lat"),
                    "lon": country_data.get("lon"),
                    "boundingbox": country_data.get("boundingbox"),
                    "geojson": country_data.get("geojson"),
                    "importance": country_data.get("importance"),
                    "osm_type": country_data.get("osm_type"),
                    "osm_id": country_data.get("osm_id")
                })
            
            logger.info(f"Multiple countries search successful for: {q}, found {len(countries)} results")
            
            return {
                "success": True,
                "query": q,
                "count": len(countries),
                "countries": countries
            }
            
    except httpx.TimeoutException:
        logger.error(f"Timeout lors de la recherche des pays: {q}")
        raise HTTPException(
            status_code=408, 
            detail="Timeout lors de la recherche. Veuillez réessayer."
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Erreur HTTP lors de la recherche des pays {q}: {e}")
        raise HTTPException(
            status_code=502, 
            detail="Erreur lors de la communication avec le service de géolocalisation"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la recherche des pays {q}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur interne du serveur: {str(e)}"
        )




