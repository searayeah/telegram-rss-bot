import requests

from bot.helper.rss_utils.reddit import HTTP_OK, REDDIT_LINK, RedditPost


def get_reddit_posts_json(
    subreddit: str, time_period: str = "month", limit: int = 100
) -> list[RedditPost]:
    url = f"{REDDIT_LINK}/r/{subreddit}/top.json?t={time_period}&limit={limit}"
    headers = {"User-Agent": "RedditBot/1.0"}  # Custom User-Agent to prevent blocks
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != HTTP_OK:
        error_message = f"Failed to fetch data from {url}: HTTP {response.status_code}"
        raise ValueError(error_message)

    data = response.json()
    posts = []

    for post in data["data"]["children"]:
        post_data = post["data"]
        posts.append(
            RedditPost(
                title=post_data["title"],
                link=f"{REDDIT_LINK}{post_data['permalink']}",
                author=post_data["author"],
                score=post_data["score"],
                num_comments=post_data["num_comments"],
                created_utc=post_data["created_utc"],
                subreddit=post_data["subreddit"],
                selftext=post_data["selftext"],
                link_flair_text=post_data["link_flair_text"],
            )
        )

    return posts


# # Example usage
# if __name__ == "__main__":
#     subreddit_name = "python"
#     posts = get_reddit_posts_json(subreddit_name, time_period="month")
#     print(len(posts))
#     for post in posts[:5]:  # Display the top 5 posts
#         print(post)
#         print(
#             f"Title: {post['title']}\nLink: {post['link']}\nAuthor: {post['author']}\nScore: {post['score']}\nComments: {post['num_comments']}\n"
#         )
