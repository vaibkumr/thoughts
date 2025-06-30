import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
import datetime

class HTMLRenderer:
    def __init__(self, data, static_dir: Path, templates_dir: Path):
        self.data = data
        self.static_dir = static_dir
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

    def render(self):
        self.static_dir.mkdir(exist_ok=True)
        
        thoughts = self._prepare_thoughts()
        
        self._generate_css()
        self._generate_index_page(thoughts)
        self._generate_categories_page(thoughts)
        self._generate_sentiment_page(thoughts)

    def _prepare_thoughts(self):
        # This is based on the provided example_output.json
        # It's not ideal as it loses original thought metadata like timestamps.
        # We'll add a fake timestamp for demonstration.
        thoughts = []
        for i, (content, details) in enumerate(self.data.get("classification", {}).items()):
            details['content'] = content
            # Add a fake timestamp for chart demonstration
            details['created_at'] = datetime.datetime.now() - datetime.timedelta(days=i)
            thoughts.append(details)
        return thoughts

    def _generate_css(self):
        template = self.env.get_template('style.css')
        css_content = template.render()
        with open(self.static_dir / "style.css", "w") as f:
            f.write(css_content)

    def _generate_index_page(self, thoughts):
        template = self.env.get_template('index.html')
        html_content = template.render(
            title="Thought Feed",
            thoughts=thoughts,
            active_page='feed'
        )
        with open(self.static_dir / "index.html", "w") as f:
            f.write(html_content)

    def _generate_categories_page(self, thoughts):
        categories = defaultdict(list)
        for thought in thoughts:
            category = thought.get('category', 'Uncategorized')
            categories[category].append(thought)
            
        template = self.env.get_template('categories.html')
        html_content = template.render(
            title="Categories",
            categories=categories,
            active_page='categories'
        )
        with open(self.static_dir / "categories.html", "w") as f:
            f.write(html_content)

    def _generate_sentiment_page(self, thoughts):
        # Sort thoughts by date for the timeseries chart
        thoughts_with_date = [t for t in thoughts if t.get('created_at')]
        thoughts_with_date.sort(key=lambda x: x.get('created_at'))

        labels = [t.get('created_at').strftime('%Y-%m-%d') for t in thoughts_with_date]
        
        sentiment_map = {"positive": 1, "neutral": 0, "ambivalent": 0, "negative": -1}
        sentiment_scores = [sentiment_map.get(t.get('sentiment', 'None'), 0) for t in thoughts_with_date]

        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": "Sentiment Score",
                "data": sentiment_scores,
                "borderColor": 'rgba(75, 192, 192, 1)',
                "backgroundColor": 'rgba(75, 192, 192, 0.2)',
                "fill": True,
            }]
        }

        template = self.env.get_template('sentiment.html')
        html_content = template.render(
            title="Sentiment Analysis",
            chart_data=json.dumps(chart_data),
            active_page='sentiment'
        )
        with open(self.static_dir / "sentiment.html", "w") as f:
            f.write(html_content) 