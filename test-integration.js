#!/usr/bin/env node

/**
 * Script de test pour l'intégration Django + Next.js
 * Ce script teste tous les endpoints d'authentification
 */

const API_BASE_URL = 'http://localhost:8001/api/auth';

// Fonction pour faire des requêtes HTTP
async function makeRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`❌ Erreur API (${endpoint}):`, error.message);
    throw error;
  }
}

// Tests d'authentification
async function testAuthentication() {
  console.log('🚀 Test de l\'intégration Django + Next.js');
  console.log('='.repeat(60));

  let accessToken = null;
  let refreshToken = null;

  try {
    // 1. Test d'inscription
    console.log('\n1️⃣ Test d\'inscription d\'un nouvel utilisateur');
    const registrationData = {
      email: 'test@dip.com',
      username: 'testuser',
      first_name: 'Test',
      last_name: 'User',
      password: 'TestPassword123!',
      password_confirm: 'TestPassword123!',
      phone: '+225 0123456789',
      organization: 'DIP Test Organization',
      role: 'user'
    };

    try {
      const registerResponse = await makeRequest('/register/', {
        method: 'POST',
        body: JSON.stringify(registrationData),
      });
      
      console.log('✅ Inscription réussie');
      console.log(`   Utilisateur: ${registerResponse.user.email}`);
      console.log(`   Rôle: ${registerResponse.user.role}`);
      
      accessToken = registerResponse.access;
      refreshToken = registerResponse.refresh;
    } catch (error) {
      if (error.message.includes('already exists')) {
        console.log('⚠️  Utilisateur déjà existant, test de connexion...');
      } else {
        throw error;
      }
    }

    // 2. Test de connexion
    console.log('\n2️⃣ Test de connexion');
    const loginData = {
      email: 'test@dip.com',
      password: 'TestPassword123!'
    };

    const loginResponse = await makeRequest('/login/', {
      method: 'POST',
      body: JSON.stringify(loginData),
    });

    console.log('✅ Connexion réussie');
    console.log(`   Utilisateur: ${loginResponse.user.email}`);
    console.log(`   Rôle: ${loginResponse.user.role}`);
    
    accessToken = loginResponse.access;
    refreshToken = loginResponse.refresh;

    // Headers avec authentification
    const authHeaders = {
      'Authorization': `Bearer ${accessToken}`
    };

    // 3. Test de récupération du profil
    console.log('\n3️⃣ Test de récupération du profil');
    const profileResponse = await makeRequest('/profile/', {
      headers: authHeaders
    });

    console.log('✅ Profil récupéré');
    console.log(`   Nom complet: ${profileResponse.first_name} ${profileResponse.last_name}`);
    console.log(`   Email: ${profileResponse.email}`);
    console.log(`   Rôle: ${profileResponse.role}`);

    // 4. Test de mise à jour du profil
    console.log('\n4️⃣ Test de mise à jour du profil');
    const updateData = {
      first_name: 'Test Updated',
      last_name: 'User Updated',
      phone: '+225 0987654321',
      organization: 'DIP Updated Organization'
    };

    const updateResponse = await makeRequest('/profile/update/', {
      method: 'PUT',
      headers: authHeaders,
      body: JSON.stringify(updateData),
    });

    console.log('✅ Profil mis à jour');
    console.log(`   Nouveau nom: ${updateResponse.user.first_name} ${updateResponse.user.last_name}`);

    // 5. Test de récupération des détails du profil
    console.log('\n5️⃣ Test de récupération des détails du profil');
    const detailsResponse = await makeRequest('/profile/details/', {
      headers: authHeaders
    });

    console.log('✅ Détails du profil récupérés');
    console.log(`   Langue: ${detailsResponse.language}`);
    console.log(`   Fuseau horaire: ${detailsResponse.timezone}`);
    console.log(`   Thème: ${detailsResponse.theme}`);

    // 6. Test de mise à jour des détails du profil
    console.log('\n6️⃣ Test de mise à jour des détails du profil');
    const profileUpdateData = {
      language: 'fr',
      timezone: 'Africa/Abidjan',
      currency: 'XOF',
      theme: 'dark',
      email_notifications: true,
      weekly_reports: true,
      monthly_reports: false
    };

    const detailsUpdateResponse = await makeRequest('/profile/details/update/', {
      method: 'PUT',
      headers: authHeaders,
      body: JSON.stringify(profileUpdateData),
    });

    console.log('✅ Détails du profil mis à jour');
    console.log(`   Nouveau thème: ${detailsUpdateResponse.profile.theme}`);

    // 7. Test de rafraîchissement du token
    console.log('\n7️⃣ Test de rafraîchissement du token');
    const refreshResponse = await makeRequest('/token/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh: refreshToken }),
    });

    console.log('✅ Token rafraîchi');
    console.log(`   Nouveau token: ${refreshResponse.access.substring(0, 50)}...`);

    // 8. Test de récupération de l'historique des connexions
    console.log('\n8️⃣ Test de récupération de l\'historique des connexions');
    const historyResponse = await makeRequest('/login-history/', {
      headers: authHeaders
    });

    console.log('✅ Historique des connexions récupéré');
    console.log(`   Nombre de tentatives: ${historyResponse.total}`);

    // 9. Test de déconnexion
    console.log('\n9️⃣ Test de déconnexion');
    const logoutResponse = await makeRequest('/logout/', {
      method: 'POST',
      headers: authHeaders,
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    console.log('✅ Déconnexion réussie');

    console.log('\n' + '='.repeat(60));
    console.log('🎉 Tous les tests d\'authentification sont passés avec succès !');
    console.log('✅ L\'intégration Django + Next.js fonctionne parfaitement');
    console.log('='.repeat(60));

  } catch (error) {
    console.log('\n' + '='.repeat(60));
    console.log('❌ Erreur lors des tests:', error.message);
    console.log('💡 Vérifiez que le serveur Django est démarré sur le port 8001');
    console.log('💡 Commande: python manage.py runserver 8001');
    console.log('='.repeat(60));
    process.exit(1);
  }
}

// Exécuter les tests
if (require.main === module) {
  testAuthentication().catch(console.error);
}

module.exports = { testAuthentication };

