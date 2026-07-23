<?php
require_once 'includes/db.php';
session_start();

$error = '';
if($_SERVER['REQUEST_METHOD'] == 'POST') {
    $email = trim($_POST['email']);
    $password = $_POST['password'];

    $stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $user = $stmt->fetch();

    if($user && password_verify($password, $user->password)) {
        $_SESSION['user_id'] = $user->id;
        $_SESSION['name'] = $user->name;
        $_SESSION['role'] = $user->role;
        header("Location: index.php");
        exit;
    } else {
        $error = "Invalid email or password.";
    }
}

require_once 'includes/header.php';
?>

<div class="container section">
    <div style="max-width: 400px; margin: 0 auto;">
        <div class="glass-panel text-center">
            <h2 class="mb-2">Welcome Back</h2>
            <p class="mb-4 text-gray-500">Log in to manage your trips</p>
            
            <?php if($error): ?>
                <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
            <?php endif; ?>

            <form method="POST" action="login.php" style="text-align: left;">
                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" name="email" class="form-control" required placeholder="john@example.com">
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Login</button>
            </form>
            
            <p class="mt-4">Don't have an account? <a href="register.php">Sign up</a></p>
            <p style="font-size: 0.8rem; margin-top: 10px; color: var(--gray-500)">Test Admin: admin@tms.com | password123</p>
            <p style="font-size: 0.8rem; color: var(--gray-500)">Test User: john@example.com | password123</p>
        </div>
    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
