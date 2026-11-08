- name: Commit and Push Generated Assets
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action Bot"
          if [ -d "production_output" ]; then
            git add production_output/
            git status
            git diff-index --quiet HEAD || git commit -m "Automated AI Content Bundle (JSON, TTS Audio & Pixabay Videos)"
            git push origin main
          else
            echo "⚠️ production_output directory not found, skipping commit."
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}