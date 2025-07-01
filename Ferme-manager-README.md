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
body {
  margin: 0;
  font-family: Arial, sans-serif;
  display: flex;
}
.sidebar {
  width: 220px;
  background: #2f3e46;
  color: #fff;
  min-height: 100vh;
  padding: 20px;
}
.sidebar h2 {
  margin-bottom: 30px;
}
.sidebar button {
  display: block;
  background: none;
  border: none;
  color: inherit;
  padding: 10px 0;
  text-align: left;
  cursor: pointer;
  width: 100%;
}
.sidebar button:hover {
  background: #354f52;
}
main {
  flex: 1;
  padding: 20px;
}
section {
  display: none;
}
section.active {
  display: block;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
th, td {
  border: 1px solid #999;
  padding: 8px;
  text-align: left;
}
button {
  margin: 5px;
  padding: 6px 12px;
  cursor: pointer;
}
