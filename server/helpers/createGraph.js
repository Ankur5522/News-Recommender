const neo4j = require('neo4j-driver');
const News = require('../schema/schema');
const cron = require('node-cron');

// Set up Neo4j driver and session
const driver = neo4j.driver('bolt://localhost:7687', neo4j.auth.basic('neo4j', 'test_password'));
const session = driver.session();

// Simple userId for now (you can change this later to dynamically fetch user info)
const userId = 'user123'; 

async function createGraphFromData() {
    try {
        // Fetch all the news articles from MongoDB
        const newsArticles = await News.find();

        // Iterate over the news articles to create nodes and relationships in Neo4j
        for (const article of newsArticles) {
            // Create a node for each article in Neo4j
            await session.run(
                `MERGE (a:Article {url: $url, createdAt: $createdAt})
                 SET a.timeSpent = $timeSpent`,
                {
                    url: article.url,
                    timeSpent: article.timeSpent,
                    createdAt: article.createdAt
                }
            );

            // Normalize the timeSpent to be between 0 and 1 (you can change the normalization logic)
            const normalizedWeight = article.timeSpent / 100; // Simple normalization (you can adjust this)

            // Create or merge a user node (for now using the static userId)
            await session.run(
                `MERGE (u:User {id: $userId})`,
                { userId: userId }
            );

            // Create a relationship between the user and the article with the normalized weight
            await session.run(
                `MATCH (u:User {id: $userId}), (a:Article {url: $url})
                 MERGE (u)-[:INTERACTED_WITH {weight: $weight}]->(a)`,
                { userId: userId, url: article.url, weight: normalizedWeight }
            );

            // Iterate over tags and create nodes and relationships for each tag
            for (const tag of article.tags) {
                // Merge the tag node (to ensure no duplicates)
                await session.run(
                    `MERGE (t:Tag {name: $tagName})`,
                    { tagName: tag.tag }
                );

                // Create a relationship between the article and the tag
                await session.run(
                    `MATCH (a:Article {url: $url}), (t:Tag {name: $tagName})
                     MERGE (a)-[:HAS_TAG]->(t)`,
                    { url: article.url, tagName: tag.tag }
                );
            }
        }

        console.log('Graph creation completed successfully.');
    } catch (error) {
        console.error('Error creating the graph:', error);
    } finally {
        // Close the Neo4j session
        await session.close();
    }
}

// Set up cron job to run every day at 12:00
// cron.schedule('0 12 * * *', () => {
//     console.log('Running graph creation process at 12:00...');
//     createGraphFromData().then(() => {
//         console.log('Graph creation process is finished.');
//     }).catch(err => {
//         console.error('Error during graph creation process:', err);
//     });
// });

// console.log('Scheduled task is running...');

module.exports = createGraphFromData;
