          {/* Paramètres de transformation */}
          <div className="bg-gradient-to-br from-white to-slate-50 rounded-2xl border border-slate-200 shadow-lg mb-8 overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-600 to-cyan-600 px-6 py-5">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                  <FiSettings className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Paramètres de transformation</h2>
                  <p className="text-blue-100 text-sm mt-1">Configurez le traitement automatique de vos données</p>
                </div>
              </div>
            </div>
              
            <div className="p-8">
              {/* Mode de traitement */}
              <div className="mb-8">
                <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                      <FiZap className="w-4 h-4 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900">Mode de traitement</h3>
                  </div>
                  <p className="text-sm text-slate-600 mb-4">Choisissez le niveau d'automatisation du traitement</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <label className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                      txOptions.processing_mode === 'automatic' 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-slate-200 hover:border-slate-300'
                    }`}>
                      <input 
                        type="radio" 
                        name="processing_mode"
                        value="automatic"
                        checked={txOptions.processing_mode === 'automatic'}
                        onChange={(e) => setTxOptions(o => ({...o, processing_mode: e.target.value}))}
                        className="sr-only"
                      />
                      <div className="text-center">
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                          <FiZap className="w-4 h-4 text-blue-600" />
                        </div>
                        <h4 className="font-semibold text-slate-900">Automatique</h4>
                        <p className="text-xs text-slate-600 mt-1">Traitement entièrement automatisé</p>
                      </div>
                    </label>
                    
                    <label className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                      txOptions.processing_mode === 'hybrid' 
                        ? 'border-purple-500 bg-purple-50' 
                        : 'border-slate-200 hover:border-slate-300'
                    }`}>
                      <input 
                        type="radio" 
                        name="processing_mode"
                        value="hybrid"
                        checked={txOptions.processing_mode === 'hybrid'}
                        onChange={(e) => setTxOptions(o => ({...o, processing_mode: e.target.value}))}
                        className="sr-only"
                      />
                      <div className="text-center">
                        <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                          <FiSettings className="w-4 h-4 text-purple-600" />
                        </div>
                        <h4 className="font-semibold text-slate-900">Hybride</h4>
                        <p className="text-xs text-slate-600 mt-1">Automatique + contrôles avancés</p>
                      </div>
                    </label>
                    
                    <label className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                      txOptions.processing_mode === 'manual' 
                        ? 'border-green-500 bg-green-50' 
                        : 'border-slate-200 hover:border-slate-300'
                    }`}>
                      <input 
                        type="radio" 
                        name="processing_mode"
                        value="manual"
                        checked={txOptions.processing_mode === 'manual'}
                        onChange={(e) => setTxOptions(o => ({...o, processing_mode: e.target.value}))}
                        className="sr-only"
                      />
                      <div className="text-center">
                        <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                          <FiEdit3 className="w-4 h-4 text-green-600" />
                        </div>
                        <h4 className="font-semibold text-slate-900">Manuel</h4>
                        <p className="text-xs text-slate-600 mt-1">Configuration détaillée</p>
                      </div>
                    </label>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {/* Valeurs manquantes */}
                <div className="group">
                  <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 group-hover:border-red-300">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                        <FiAlertCircle className="w-4 h-4 text-red-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900">Valeurs manquantes</h3>
                    </div>
                    <p className="text-sm text-slate-600 mb-4">Gestion des données incomplètes</p>
                    <div className="space-y-4">
                      <select 
                        className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm bg-white shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-all duration-200 hover:border-slate-400" 
                        value={txOptions.missing_strategy}
                        onChange={(e) => setTxOptions(o => ({...o, missing_strategy: e.target.value}))}
                      >
                        <option value="none">Aucun traitement</option>
                        <option value="drop">Supprimer les lignes</option>
                        <option value="mean">Remplacer par moyenne</option>
                        <option value="median">Remplacer par médiane</option>
                        <option value="mode">Remplacer par mode</option>
                        <option value="knn">Interpolation KNN</option>
                        <option value="group_mean">Moyenne par groupe</option>
                      </select>
                      
                      {txOptions.missing_strategy === 'group_mean' && (
                        <div className="mt-3">
                          <label className="block text-sm font-medium text-slate-700 mb-2">Colonne de groupement</label>
                          <select 
                            className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm bg-white shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
                            value={txOptions.group_by}
                            onChange={(e) => setTxOptions(o => ({...o, group_by: e.target.value}))}
                          >
                            <option value="">Sélectionner une colonne</option>
                            {columns.map(col => (
                              <option key={col} value={col}>{col}</option>
                            ))}
                          </select>
                        </div>
                      )}
                      
                      <div className="mt-3">
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Seuil de suppression ({txOptions.missing_threshold * 100}%)
                        </label>
                        <input 
                          type="range" 
                          min="0" 
                          max="1" 
                          step="0.1"
                          value={txOptions.missing_threshold}
                          onChange={(e) => setTxOptions(o => ({...o, missing_threshold: parseFloat(e.target.value)}))}
                          className="w-full"
                        />
                        <p className="text-xs text-slate-500 mt-1">
                          Colonnes avec plus de {txOptions.missing_threshold * 100}% de valeurs manquantes seront supprimées
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Valeurs aberrantes */}
                <div className="group">
                  <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 group-hover:border-orange-300">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                        <FiTarget className="w-4 h-4 text-orange-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900">Valeurs aberrantes</h3>
                    </div>
                    <p className="text-sm text-slate-600 mb-4">Détection et traitement des outliers</p>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Méthode de détection</label>
                        <select 
                          className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm bg-white shadow-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all duration-200 hover:border-slate-400" 
                          value={txOptions.outlier_detection}
                          onChange={(e) => setTxOptions(o => ({...o, outlier_detection: e.target.value}))}
                        >
                          <option value="iqr">Méthode IQR</option>
                          <option value="zscore">Score Z</option>
                          <option value="isolation_forest">Isolation Forest</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Méthode de traitement</label>
                        <select 
                          className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm bg-white shadow-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all duration-200 hover:border-slate-400" 
                          value={txOptions.outliers_method}
                          onChange={(e) => setTxOptions(o => ({...o, outliers_method: e.target.value}))}
                        >
                          <option value="winsorize">Winsorisation</option>
                          <option value="cap">Capping aux percentiles</option>
                          <option value="remove">Supprimer les outliers</option>
                          <option value="transform">Transformation logarithmique</option>
                        </select>
                      </div>
                      
                      <label className="flex items-center space-x-3 p-3 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors duration-200">
                        <input 
                          type="checkbox" 
                          className="w-4 h-4 text-orange-600 border-slate-300 rounded focus:ring-orange-500" 
                          checked={txOptions.handle_outliers}
                          onChange={(e) => setTxOptions(o => ({...o, handle_outliers: e.target.checked}))} 
                        />
                        <span className="text-sm font-medium text-slate-700">Activer la détection</span>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Nettoyage des données */}
                <div className="group">
                  <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 group-hover:border-green-300">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <FiRefreshCw className="w-4 h-4 text-green-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900">Nettoyage des données</h3>
                    </div>
                    <p className="text-sm text-slate-600 mb-4">Amélioration de la qualité des données</p>
                    <div className="space-y-3">
                      <label className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors duration-200">
                        <input 
                          type="checkbox" 
                          className="w-4 h-4 text-green-600 border-slate-300 rounded focus:ring-green-500" 
                          checked={txOptions.remove_duplicates}
                          onChange={(e) => setTxOptions(o => ({...o, remove_duplicates: e.target.checked}))} 
                        />
                        <span className="text-sm font-medium text-slate-700">Supprimer les doublons</span>
                      </label>
                      <label className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors duration-200">
                        <input 
                          type="checkbox" 
                          className="w-4 h-4 text-green-600 border-slate-300 rounded focus:ring-green-500" 
                          checked={txOptions.fix_inconsistencies}
                          onChange={(e) => setTxOptions(o => ({...o, fix_inconsistencies: e.target.checked}))} 
                        />
                        <span className="text-sm font-medium text-slate-700">Corriger les incohérences</span>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Normalisation numérique */}
                <div className="group">
                  <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 group-hover:border-blue-300">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FiBarChart2 className="w-4 h-4 text-blue-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900">Normalisation numérique</h3>
                    </div>
                    <p className="text-sm text-slate-600 mb-4">Standardisation des valeurs numériques</p>
                    <div className="space-y-4">
                      <label className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200">
                        <input 
                          type="checkbox" 
                          className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500" 
                          checked={txOptions.normalize_numerical}
                          onChange={(e) => setTxOptions(o => ({...o, normalize_numerical: e.target.checked}))} 
                        />
                        <span className="text-sm font-medium text-slate-700">Activer la normalisation</span>
                      </label>
                      
                      <select
                        className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 hover:border-slate-400" 
                        value={txOptions.numerical_method}
                        onChange={(e) => setTxOptions(o => ({...o, numerical_method: e.target.value}))}
                      >
                        <option value="standard">Standardisation (Z-score)</option>
                        <option value="minmax">Min-Max Scaling</option>
                        <option value="robust">Robust Scaling</option>
                        <option value="normal">Normalisation simple</option>
                      </select>
                      
                      <label className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200">
                        <input 
                          type="checkbox" 
                          className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500" 
                          checked={txOptions.normalize_by_group}
                          onChange={(e) => setTxOptions(o => ({...o, normalize_by_group: e.target.checked}))} 
                        />
                        <span className="text-sm font-medium text-slate-700">Normalisation par groupe</span>
                      </label>
                      
                      {txOptions.normalize_by_group && (
                        <div className="mt-3">
                          <label className="block text-sm font-medium text-slate-700 mb-2">Méthode de groupement</label>
                          <select 
                            className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            value={txOptions.group_normalization_method}
                            onChange={(e) => setTxOptions(o => ({...o, group_normalization_method: e.target.value}))}
                          >
                            <option value="minmax">Min-Max par groupe</option>
                            <option value="standard">Standardisation par groupe</option>
                          </select>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Encodage des catégories */}
                <div className="group">
                  <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 group-hover:border-purple-300">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                        <FiGrid className="w-4 h-4 text-purple-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900">Encodage des catégories</h3>
                    </div>
                    <p className="text-sm text-slate-600 mb-4">Conversion des données catégorielles</p>
                    <div className="space-y-4">
                      <label className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors duration-200">
                        <input 
                          type="checkbox" 
                          className="w-4 h-4 text-purple-600 border-slate-300 rounded focus:ring-purple-500" 
                          checked={txOptions.encode_categorical}
                          onChange={(e) => setTxOptions(o => ({...o, encode_categorical: e.target.checked}))} 
                        />
                        <span className="text-sm font-medium text-slate-700">Activer l'encodage</span>
                      </label>
                      
                      <select 
                        className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm bg-white shadow-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 hover:border-slate-400" 
                        value={txOptions.categorical_method}
                        onChange={(e) => setTxOptions(o => ({...o, categorical_method: e.target.value}))}
                      >
                        <option value="label">Encodage par étiquette</option>
                        <option value="onehot">One-hot encoding</option>
                        <option value="frequency">Encodage par fréquence</option>
                      </select>
                      
                      <div className="mt-3">
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Limite de catégories pour One-hot ({txOptions.max_categories})
                        </label>
                        <input 
                          type="range" 
                          min="10" 
                          max="100" 
                          step="10"
                          value={txOptions.max_categories}
                          onChange={(e) => setTxOptions(o => ({...o, max_categories: parseInt(e.target.value)}))}
                          className="w-full"
                        />
                        <p className="text-xs text-slate-500 mt-1">
                          Au-delà de {txOptions.max_categories} catégories, l'encodage par étiquette sera utilisé
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Traitement des dates */}
                <div className="group">
                  <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 group-hover:border-indigo-300">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
                        <FiCalendar className="w-4 h-4 text-indigo-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900">Traitement des dates</h3>
                    </div>
                    <p className="text-sm text-slate-600 mb-4">Standardisation des formats de dates</p>
                    <div className="space-y-3">
                      <label className="flex items-center space-x-3 p-3 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors duration-200">
                        <input 
                          type="checkbox" 
                          className="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500" 
                          checked={txOptions.normalize_dates}
                          onChange={(e) => setTxOptions(o => ({...o, normalize_dates: e.target.checked}))} 
                        />
                        <span className="text-sm font-medium text-slate-700">Normaliser les formats de dates</span>
                      </label>
                      
                      <label className="flex items-center space-x-3 p-3 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors duration-200">
                        <input 
                          type="checkbox" 
                          className="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500" 
                          checked={txOptions.extract_date_features}
                          onChange={(e) => setTxOptions(o => ({...o, extract_date_features: e.target.checked}))} 
                        />
                        <span className="text-sm font-medium text-slate-700">Extraire les features temporelles</span>
                      </label>
                      
                      <div className="mt-3">
                        <label className="block text-sm font-medium text-slate-700 mb-2">Format de sortie</label>
                        <select 
                          className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm bg-white shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                          value={txOptions.date_format}
                          onChange={(e) => setTxOptions(o => ({...o, date_format: e.target.value}))}
                        >
                          <option value="%Y-%m-%d">YYYY-MM-DD</option>
                          <option value="%d/%m/%Y">DD/MM/YYYY</option>
                          <option value="%m/%d/%Y">MM/DD/YYYY</option>
                          <option value="%Y-%m-%d %H:%M:%S">YYYY-MM-DD HH:MM:SS</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Transformations avancées */}
                <div className="group md:col-span-2 lg:col-span-3">
                  <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 group-hover:border-teal-300">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-8 h-8 bg-teal-100 rounded-lg flex items-center justify-center">
                        <FiTrendingUp className="w-4 h-4 text-teal-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900">Transformations avancées</h3>
                    </div>
                    <p className="text-sm text-slate-600 mb-6">Transformations mathématiques et statistiques</p>
                    
                    <div className="space-y-6">
                      <label className="flex items-center space-x-3 p-4 bg-teal-50 rounded-xl hover:bg-teal-100 transition-colors duration-200">
                        <input 
                          type="checkbox" 
                          className="w-5 h-5 text-teal-600 border-slate-300 rounded focus:ring-teal-500" 
                          checked={txOptions.apply_transformations}
                          onChange={(e) => setTxOptions(o => ({...o, apply_transformations: e.target.checked}))} 
                        />
                        <span className="text-sm font-semibold text-slate-700">Activer les transformations</span>
                      </label>
                      
                      {txOptions.apply_transformations && (
                        <div className="bg-slate-50 rounded-xl p-4 space-y-4">
                          <div>
                            <label className="block text-sm font-semibold text-slate-700 mb-3">Types de transformations</label>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                              {['log', 'boxcox', 'sqrt', 'square'].map(transform => (
                                <label key={transform} className="flex items-center space-x-2 p-2 bg-white rounded-lg hover:bg-slate-50">
                                  <input 
                                    type="checkbox" 
                                    className="w-4 h-4 text-teal-600 border-slate-300 rounded focus:ring-teal-500"
                                    checked={txOptions.transformations.includes(transform)}
                                    onChange={(e) => {
                                      const newTransforms = e.target.checked 
                                        ? [...txOptions.transformations, transform]
                                        : txOptions.transformations.filter(t => t !== transform);
                                      setTxOptions(o => ({...o, transformations: newTransforms}));
                                    }}
                                  />
                                  <span className="text-sm text-slate-700 capitalize">{transform}</span>
                                </label>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <label className="block text-sm font-semibold text-slate-700 mb-3">Colonnes à transformer</label>
                            <select
                              multiple 
                              className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm min-h-[120px] bg-white shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                              value={txOptions.transform_columns as any}
                              onChange={(e) => {
                                const selected = Array.from(e.target.selectedOptions).map(o => o.value);
                                setTxOptions(o => ({...o, transform_columns: selected}));
                              }}
                            >
                              {columns.filter(col => data?.columns?.some((c: any) => c.name === col && c.type === 'numeric')).map(c => (
                                <option key={c} value={c}>{c}</option>
                              ))}
                            </select>
                            <p className="text-xs text-slate-500 mt-2">Maintenez Ctrl (Cmd sur Mac) pour sélectionner plusieurs colonnes</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Bouton d'action */}
              <div className="mt-8 pt-6 border-t border-slate-200">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div className="text-sm text-slate-600">
                      Les paramètres seront appliqués lors de la prochaine transformation
                    </div>
                  </div>
                  <button 
                    onClick={handleTransform}
                    disabled={isTransforming}
                    className="group relative inline-flex items-center px-6 py-3 border border-transparent rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                  >
                    {isTransforming ? (
                      <>
                        <FiLoader className="w-5 h-5 mr-3 animate-spin" />
                        Transformation en cours...
                      </>
                    ) : (
                      <>
                        <FiRefreshCw className="w-5 h-5 mr-3 group-hover:rotate-180 transition-transform duration-300" />
                        Appliquer les transformations
                      </>
                    )}
                    
                    {/* Effet de brillance */}
                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  </button>
                </div>
              </div>
            </div>
          </div>
