index.html
assets/
  css/style.css
  js/app.js
  <!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Ferme Manager</title>
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
  <aside class="sidebar">
    <h2>Ferme Manager</h2>
    <nav>
      <ul>
        <li><button data-section="dashboard">Dashboard</button></li>
        <li><button data-section="stocks">Stocks</button></li>
        <li><button data-section="elevages">Élevages</button></li>
        <li><button data-section="employes">Employés</button></li>
      </ul>
    </nav>
  </aside>
  <main id="main-content">
    <!-- Sections dynamiques injectées par JS -->
  </main>
  <script src="assets/js/app.js"></script>
</body>
</html>
