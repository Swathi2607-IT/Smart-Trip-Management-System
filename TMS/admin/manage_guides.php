<?php
require_once 'header.php';

// Handle Guide Addition
if($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['add_guide'])) {
    $name = trim($_POST['name']);
    $email = trim($_POST['email']);
    $phone = trim($_POST['phone']);
    $langs = trim($_POST['languages']);
    
    $iStmt = $pdo->prepare("INSERT INTO guides (name, email, phone, languages) VALUES (?, ?, ?, ?)");
    $iStmt->execute([$name, $email, $phone, $langs]);
    $msg = "Guide '$name' has been added directly to the system.";
}

// Fetch all guides
$gStmt = $pdo->query("SELECT * FROM guides");
$guides = $gStmt->fetchAll();
?>

<div class="container section">

    <?php if(isset($msg)): ?>
        <div class="alert alert-success"><?= htmlspecialchars($msg) ?></div>
    <?php endif; ?>

    <div class="grid" style="grid-template-columns: 1fr 2fr; gap: 2rem;">
        
        <div>
            <div class="glass-panel text-left">
                <h3 class="mb-4">Add a New Guide</h3>
                <form method="POST" action="manage_guides.php">
                    <div class="form-group">
                        <label class="form-label">Full Name</label>
                        <input type="text" name="name" class="form-control" required placeholder="Alice Wonderland">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Email Address</label>
                        <input type="email" name="email" class="form-control" required placeholder="alice@tms.com">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Phone Number</label>
                        <input type="text" name="phone" class="form-control" required placeholder="(+91)">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Fluent Languages</label>
                        <input type="text" name="languages" class="form-control" required placeholder="English, French, Hindi">
                    </div>
                    
                    <button type="submit" name="add_guide" class="btn btn-primary" style="width: 100%;">Create Guide Profile</button>
                </form>
            </div>
        </div>

        <div>
            <h2 class="mb-4">Registered Tour Guides</h2>
            <div class="grid grid-cols-2 text-left">
                <?php foreach($guides as $g): ?>
                    <div class="glass-panel" style="padding: 1.5rem;">
                        <h3 class="mb-2" style="display: flex; align-items: center; gap: 10px;">
                            <span style="background: var(--gray-200); padding: 5px 10px; border-radius: 50%;">👨‍✈️</span>
                            <?= htmlspecialchars($g->name) ?>
                        </h3>
                        <p class="mb-1 text-gray-500" style="font-size: 0.9rem;">📧 <?= htmlspecialchars($g->email) ?></p>
                        <p class="mb-1 text-gray-500" style="font-size: 0.9rem;">📞 <?= htmlspecialchars($g->phone) ?></p>
                        <p class="mb-1" style="font-size: 0.9rem;"><strong>Languages:</strong> <?= htmlspecialchars($g->languages) ?></p>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
        
    </div>
</div>

</main>
</body>
</html>
