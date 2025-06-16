<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LHC Proton Collision Animation</title>
    <style>
        body { margin: 0; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.134.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 20, 50);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // Orbit controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.update();

        // Starry background
        const starGeometry = new THREE.BufferGeometry();
        const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.1 });
        const starPositions = new Float32Array(1000 * 3);
        for (let i = 0; i < 1000; i++) {
            starPositions[i * 3] = (Math.random() - 0.5) * 200;
            starPositions[i * 3 + 1] = (Math.random() - 0.5) * 200;
            starPositions[i * 3 + 2] = (Math.random() - 0.5) * 200;
        }
        starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
        const stars = new THREE.Points(starGeometry, starMaterial);
        scene.add(stars);

        // Lighting
        const light = new THREE.PointLight(0xffffff, 1, 100);
        light.position.set(0, 0, 0);
        scene.add(light);

        // Detector (CMS-like cylinder)
        const detectorRadius = 15;
        const detectorLength = 30;
        const detectorGeometry = new THREE.CylinderGeometry(detectorRadius, detectorRadius, detectorLength, 32, 1, true);
        const detectorMaterial = new THREE.MeshBasicMaterial({ color: 0x333333, wireframe: true, transparent: true, opacity: 0.3 });
        const detector = new THREE.Mesh(detectorGeometry, detectorMaterial);
        detector.rotation.z = Math.PI / 2;
        scene.add(detector);

        // Proton beams
        const protonRadius = 0.5;
        const protonMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 }); // Red for protons
        const proton1 = new THREE.Mesh(new THREE.SphereGeometry(protonRadius, 16, 16), protonMaterial);
        const proton2 = new THREE.Mesh(new THREE.SphereGeometry(protonRadius, 16, 16), protonMaterial);
        scene.add(proton1, proton2);
        let protonTime = 0;
        let collisionOccurred = false;

        // Particle tracks
        const tracks = [];
        const numTracks = 20;
        const B = 4; // 4 T magnetic field
        const c = 3e8; // Speed of light (m/s)
        const q = 1.6e-19; // Charge (C)
        const colors = [0x00ffff, 0xff00ff, 0xffff00, 0x00ff00, 0xffa500]; // Neon: cyan, magenta, yellow, green, orange

        function createTrack() {
            const pT = 1 + Math.random() * 10; // p_T: 1–10 GeV/c
            const phi = Math.random() * 2 * Math.PI;
            const theta = Math.acos(2 * Math.random() - 1);
            const radius = (pT * 1e9 * c) / (q * B * 1e9); // Cyclotron radius, scaled
            const vz = pT * Math.cos(theta) * c;
            const lifetime = 2 + Math.random(); // 2–3 s
            const color = colors[Math.floor(Math.random() * colors.length)];
            const material = new THREE.LineBasicMaterial({ color: color });
            const points = [];
            const steps = 50;
            for (let i = 0; i < steps; i++) {
                const t = i * 0.01;
                const x = radius * Math.cos(t + phi);
                const y = radius * Math.sin(t + phi);
                const z = vz * t / 1e9;
                points.push(new THREE.Vector3(x, y, z));
                if (Math.sqrt(x*x + y*y) > detectorRadius || Math.abs(z) > detectorLength/2) break;
            }
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(geometry, material);
            scene.add(line);
            tracks.push({ line, lifetime, age: 0 });
        }

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            protonTime += 0.016; // ~60 FPS
            if (!collisionOccurred) {
                // Move protons toward origin
                const x1 = 50 - protonTime * 20; // Proton 1 from x=50
                const x2 = -50 + protonTime * 20; // Proton 2 from x=-50
                proton1.position.set(x1, 0, 0);
                proton2.position.set(x2, 0, 0);
                if (Math.abs(x1) < 0.5) { // Collision at origin
                    collisionOccurred = true;
                    scene.remove(proton1, proton2);
                    for (let i = 0; i < numTracks; i++) createTrack(); // Spawn tracks
                }
            } else {
                // Update tracks
                for (let i = tracks.length - 1; i >= 0; i--) {
                    tracks[i].age += 0.016;
                    const alpha = 1 - tracks[i].age / tracks[i].lifetime;
                    if (alpha <= 0) {
                        scene.remove(tracks[i].line);
                        tracks.splice(i, 1);
                        createTrack(); // Continuous collisions
                    } else {
                        tracks[i].line.material.opacity = alpha;
                    }
                }
            }
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        // Resize handler
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
