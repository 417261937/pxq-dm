import random
import re

with open('README.md', 'r') as f:
    content = f.read()

rand_str = '<!-- {} -->'.format(random.randint(1, 1000000000))

content = re.sub('<!-- BLOG_START -->([\s\S]*?)<!-- BLOG_END -->', f'<!-- BLOG_START -->\n{rand_str}\n<!-- BLOG_END -->', content)

with open('README.md', 'w') as f:
    f.write(content)
