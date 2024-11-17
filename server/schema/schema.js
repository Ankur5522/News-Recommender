const mongoose = require('mongoose');

const Schema = mongoose.Schema;

const newsSchema = new Schema({
    url: {
        type: String,
        required: true
    },
    category: {
        type: String,
        required: true
    },
    timeSpent: {
        type: Number,
        required: true
    },
    tags: {
        type: [Object],
        required: true
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('News', newsSchema);