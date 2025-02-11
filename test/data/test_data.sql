INSERT INTO users (user_id, name) 
VALUES 
    (1, 'Toyesh'),
    (2, 'Bob Smith'),
    (3, 'Charlie Davis'),
    (4, 'Diana Adams'),
    (5, 'user5'),
    (21, 'Toyesh singh'),
    (22, 'Ritesh'),
    (23, 'Arun');

INSERT INTO question (question_id, question, question_type, question_type_id) 
VALUES 
    (3, 'Design a function to find the intersection of two arrays.', 'Data structures and algorithm', 1),
    (4, 'Write a function to implement binary search on a sorted array.', 'Data structures and algorithm', 1),
    (5, 'Develop an algorithm to sort an array using quicksort.', 'Data structures and algorithm', 1),
    (6, 'Find the kth smallest element in a binary search tree.', 'Data structures and algorithm', 1),
    (7, 'Implement a function to detect a cycle in a graph.', 'Data structures and algorithm', 1),
    (8, 'Write a program to find the maximum subarray sum using Kadane’s algorithm.', 'Data structures and algorithm', 1),
    (9, 'Create a function to merge two sorted linked lists.', 'Data structures and algorithm', 1),
    (10, 'Design an algorithm to find all permutations of a given string.', 'Data structures and algorithm', 1),
    (1, 'What is the approach to reverse a linked list.', 'Data structures and algorithm', 1),
    (2, 'What will be the approach to check if a string is a palindrome.', 'Data structures and algorithm', 1);

INSERT INTO criterion (criterion_id, criterion, question_type_id, question_id)
VALUES
    (1, 'Are the assumptions clarified?', 1, 1),
    (2, 'Does the candidate account for corner cases?', 1, 1),
    (3, 'Does the candidate choose the appropriate data structure for the problem?', 1, 1),
    (4, 'Does the candidate select a suitable algorithm for the task?', 1, 1),
    (5, 'Does the solution proposed by the candidate have optimal time complexity?', 1, 1),
    (6, 'Does the solution proposed by the candidate have optimal space complexity?', 1, 1),
    (7, 'Does the proposed solution handle generic use cases?', 1, 1);

INSERT INTO subcriterion (subcriterion_id, subcriterion, criterion_id, question_id, weight)
VALUES
    (1510, 'Has the candidate defined what constitutes a word in the context of this problem?', 1, 3, 3),
    (1511, 'Is it clarified how to handle multiple spaces between words?', 1, 3, 4),
    (1512, 'What is the expected behavior for leading or trailing spaces?', 1, 3, 3),
    (1513, 'What happens if the input sentence is empty or null?', 2, 3, 4),
    (1514, 'How does the solution handle punctuation attached to words?', 2, 3, 3),
    (1515, 'Is there consideration for sentences with only spaces?', 2, 3, 3),
    (1516, 'Does the candidate use a list or array to store words?', 3, 3, 4),
    (1517, 'Is a stack considered for reversing the order?', 3, 3, 3),
    (1518, 'Is the choice of data structure justified in terms of performance?', 3, 3, 3),
    (1519, 'Does the candidate describe using a linear pass to split the sentence?', 4, 3, 4),
    (1520, 'Is the reversing of the list explained clearly?', 4, 3, 3),
    (1521, 'Is there a discussion on in-place versus additional structure usage for reversal?', 4, 3, 3),
    (1522, 'Is the time complexity for splitting the sentence analyzed?', 5, 3, 4),
    (1523, 'Does the candidate mention the efficiency of reversing the list?', 5, 3, 3),
    (1524, 'Is there a discussion on overall complexity compared to different methods?', 5, 3, 3),
    (1525, 'Is the space complexity for storing words discussed?', 6, 3, 4),
    (1526, 'Has the candidate considered optimizing space usage during reversal?', 6, 3, 3),
    (1527, 'What happens if the input is extremely large?', 6, 3, 3),
    (1528, 'Does the solution work for sentences with mixed casing?', 7, 3, 4),
    (1529, 'How does the proposed method handle special characters?', 7, 3, 3),
    (1530, 'Is there a plan for handling exceptionally long sentences?', 7, 3, 3),
    (1594, 'Does the candidate state assumptions about input size and data type?', 1, 5, 4),
    (1595, 'Are there clarifications about the expected output format?', 1, 5, 3),
    (1596, 'Is there a discussion on whether the array may contain duplicates?', 1, 5, 3),
    (1597, 'How does the algorithm handle an empty array?', 2, 5, 4),
    (1598, 'What happens if all elements are identical?', 2, 5, 3),
    (1599, 'Are negative numbers or special characters considered?', 2, 5, 3),
    (1600, 'Is the choice of array data structure justified?', 3, 5, 4),
    (1601, 'Does the candidate discuss the implications of using a list versus an array?', 3, 5, 3),
    (1602, 'Is there an explanation of why a particular data structure is chosen for sorting?', 3, 5, 3),
    (1603, 'Is quicksort the best choice for the provided input characteristics?', 4, 5, 4),
    (1604, 'Does the candidate explain the divide-and-conquer approach of quicksort?', 4, 5, 3),
    (1605, 'Are alternative sorting algorithms considered and compared?', 4, 5, 3),
    (1606, 'What is the average and worst-case time complexity provided?', 5, 5, 4),
    (1607, 'Does the candidate explain the impact of the pivot selection on performance?', 5, 5, 3),
    (1608, 'Is there a discussion on the time complexity of different scenarios?', 5, 5, 3),
    (1609, 'Is the space complexity of the algorithm discussed?', 6, 5, 4),
    (1610, 'Does the candidate mention in-place sorting aspects?', 6, 5, 3),
    (1611, 'Are recursive stack space considerations addressed?', 6, 5, 3),
    (1612, 'Does the solution work for various data types beyond integers?', 7, 5, 4),
    (1613, 'How does the solution handle already sorted arrays?', 7, 5, 3),
    (1614, 'Is there a consideration for very large datasets?', 7, 5, 3),
    (1531, 'Is it clear what type of linked list (singly, doubly) is being reversed?', 1, 1, 3),
    (1532, 'Are there any specific constraints on the linked list (e.g., size, node values)?', 1, 1, 3),
    (1533, 'Is the candidate aware of the implications of modifying the original list?', 1, 1, 4),
    (1534, 'What happens if the linked list is empty?', 2, 1, 4),
    (1535, 'How does the solution handle a single-node linked list?', 2, 1, 3),
    (1536, 'Are there any assumptions about the input data (e.g., all nodes are unique)?', 2, 1, 3),
    (1537, 'Is a linked list the most appropriate data structure for this problem?', 3, 1, 4),
    (1538, 'Could the candidate consider using arrays or other structures, and why?', 3, 1, 3),
    (1539, 'Does the candidate demonstrate an understanding of the characteristics of linked lists?', 3, 1, 3),
    (1540, 'What algorithm does the candidate propose for reversing the linked list?', 4, 1, 4),
    (1541, 'Does the candidate discuss both iterative and recursive approaches?', 4, 1, 3),
    (1542, 'Is there an explanation of why the chosen algorithm is preferred?', 4, 1, 3),
    (1543, 'Does the proposed solution run in linear time (O(n))?', 5, 1, 5),
    (1544, 'Is there a discussion about the time complexity of the chosen algorithm?', 5, 1, 3),
    (1545, 'Are there alternative solutions mentioned that have worse time complexity?', 5, 1, 2),
    (1546, 'Does the candidates solution use O(1) additional space?', 6, 1, 4),
    (1547, 'Is there a mention of space complexity in the explanation?', 6, 1, 3),
    (1548, 'How does the solution scale with larger linked lists in terms of memory usage?', 6, 1, 3),
    (1549, 'Does the solution handle various input scenarios (e.g., large lists, lists with cycles)?', 7, 1, 4),
    (1550, 'Is the proposed solution adaptable for different types of linked lists?', 7, 1, 3),
    (1551, 'How would the solution perform with different data types in the nodes?', 7, 1, 3),
    (1573, 'Has the candidate defined what type of graph is being used (directed/undirected)?', 1, 7, 4),
    (1574, 'Are the assumptions regarding input types and constraints clarified?', 1, 7, 3),
    (1575, 'Is there a discussion about whether the graph is cyclic or acyclic?', 1, 7, 3),
    (1576, 'Does the candidate consider an empty graph as a valid input?', 2, 7, 3),
    (1577, 'How does the solution handle graphs with a single node?', 2, 7, 4),
    (1578, 'What happens if there are multiple cycles in the graph?', 2, 7, 3),
    (1579, 'Is an adjacency list or matrix being used, and why?', 3, 7, 4),
    (1580, 'Does the candidate discuss the trade-offs of using different data structures?', 3, 7, 3),
    (1581, 'Is there consideration for the graphs density in choosing a data structure?', 3, 7, 3),
    (1582, 'Is Depth-First Search (DFS) or Breadth-First Search (BFS) being utilized, and why?', 4, 7, 4),
    (1583, 'Has the candidate considered using Union-Find as an alternative approach?', 4, 7, 3),
    (1584, 'Is there a discussion on the appropriateness of the selected algorithm for the problem size?', 4, 7, 3),
    (1585, 'What is the time complexity of the proposed solution?', 5, 7, 4),
    (1586, 'Does the candidate mention how the complexity changes with different graph representations?', 5, 7, 3),
    (1587, 'Is there a focus on improving the algorithms efficiency?', 5, 7, 3),
    (1588, 'What is the space complexity of the proposed solution?', 6, 7, 4),
    (1589, 'Does the candidate consider the memory overhead of the data structures used?', 6, 7, 3),
    (1590, 'Is there any discussion on optimizing space usage?', 6, 7, 3),
    (1591, 'Does the solution work for both small and large graphs?', 7, 7, 4),
    (1592, 'Is there consideration for disconnected graphs?', 7, 7, 3),
    (1593, 'How does the solution handle graphs with various node types or weights?', 7, 7, 3);

INSERT INTO interview (interview_id, user_id, interview_date, interview_recording_url)
VALUES
    (1, 1, '2024-12-07 16:19:28.906', 'updated URL'),
    (2, 2, '2024-12-02 11:30:00', 'https://recordings.example.com/bob_interview.mp3'),
    (3, 3, '2024-12-03 09:45:00', 'https://recordings.example.com/charlie_interview.mp3'),
    (4, 1, '2024-12-01 10:00:00', 'test_url');

INSERT INTO interview_question (interview_id, question_id)
VALUES
    (3, 3),
    (3, 2),
    (1, 2);

INSERT INTO chat_history (chat_history_turn_id, interview_id, question_id, candidate_answer)
VALUES
    (10, 1, 2, 'i will use two pointer approach to reverse the entire string character by characer including spaces repreat same reversal technique for each word'),
    (11, 2, 2, 'I want to use two pointer approach and iterate on both sides of the string while comparing each character'),
    (12, 2, 3, 'I want to use two pointer approach and iterate on both sides of the sentence and swap characters on both pointers as I iterate through the string redo the two pointer technique for each word again and that will reverse the sentence.'),
    (13, 2, 1, 'To reverse a linked list, iterate through the list while updating the next pointer of each node to point to its previous node. Maintain three pointers: prev (initially null), current (starting at the head), and next_node (to store the next node temporarily). Move through the list until current is null, ensuring edge cases like empty or single-node lists are handled. This iterative approach has O(n) time complexity and O(1) space complexity, making it efficient and scalable.'),
    (14, 2, 1, 'To reverse a linked list, iterate through the list while updating the next pointer of each node to point to its previous node. Maintain three pointers: prev (initially null), current (starting at the head), and next_node (to store the next node temporarily). Move through the list until current is null, ensuring edge cases like empty or single-node lists are handled. This iterative approach has O(n) time complexity and O(1) space complexity, making it efficient and scalable.'),
    (15, 3, 7, 'To detect a cycle in a graph, use Depth-First Search (DFS) for directed graphs or Union-Find for undirected graphs. For DFS, maintain a visited set and a recursion stack to track nodes in the current path, detecting back edges that form a cycle. For undirected graphs, Union-Find tracks connected components, detecting cycles when two nodes in the same set are connected. Handle edge cases like empty or disconnected graphs explicitly. Both approaches ensure efficient detection with O(V+E) time complexity.'),
    (16, 3, 7, 'To detect a cycle in a graph, use Depth-First Search (DFS) for directed graphs or Union-Find for undirected graphs. For DFS, maintain a visited set and a recursion stack to track nodes in the current path, detecting back edges that form a cycle. For undirected graphs, Union-Find tracks connected components, detecting cycles when two nodes in the same set are connected. Handle edge cases like empty or disconnected graphs explicitly. Both approaches ensure efficient detection with O(V+E) time complexity.'),
    (17, 3, 7, 'To detect a cycle in a graph, use Depth-First Search (DFS) for directed graphs or Union-Find for undirected graphs. For DFS, maintain a visited set and a recursion stack to track nodes in the current path, detecting back edges that form a cycle. For undirected graphs, Union-Find tracks connected components, detecting cycles when two nodes in the same set are connected. Handle edge cases like empty or disconnected graphs explicitly. Both approaches ensure efficient detection with O(V+E) time complexity.'),
    (18, 3, 7, 'To detect a cycle in a graph, use Depth-First Search (DFS) for directed graphs or Union-Find for undirected graphs. For DFS, maintain a visited set and a recursion stack to track nodes in the current path, detecting back edges that form a cycle. For undirected graphs, Union-Find tracks connected components, detecting cycles when two nodes in the same set are connected. Handle edge cases like empty or disconnected graphs explicitly. Both approaches ensure efficient detection with O(V+E) time complexity.');

INSERT INTO final_evaluation (final_evaluation_id, interview_id, final_evaluation_json, final_feedback)
VALUES
    (2, 2, '{"overall": "strong", "recommendation": "hire"}', 'Good problem-solving abilities.'),
    (3, 3, '{"overall": "average", "recommendation": "consider"}', 'Efficient DSA solutions.'),
    (7, 1, 'this is a JSON', NULL);

INSERT INTO interview_question_evaluation 
(question_evaluation_id, interview_id, question_id, score, question_evaluation_json)
VALUES
    (45, 3, 7, 5.16, '{"evaluation_results": {"3": {"metrics": {"1": "Is an adjacency list or matrix being used, and why?", "2": "Does the candidate discuss the trade-offs of using different data structures?", "3": "Is there consideration for the graphs density in choosing a data structure?"}, "responses": {"Is an adjacency list or matrix being used, and why?": "1", "Does the candidate discuss the trade-offs of using different data structures?": "1", "Is there consideration for the graphs density in choosing a data structure?": "1"}, "accumulated_result": 1.0}, "7": {"metrics": {"1": "Does the solution work for both small and large graphs?", "2": "Is there consideration for disconnected graphs?", "3": "How does the solution handle graphs with various node types or weights?"}, "responses": {"Does the solution work for both small and large graphs?": "10", "Is there consideration for disconnected graphs?": "10", "How does the solution handle graphs with various node types or weights?": "1"}, "accumulated_result": 7.3}, "4": {"metrics": {"1": "Is Depth-First Search (DFS) or Breadth-First Search (BFS) being utilized, and why?", "2": "Has the candidate considered using Union-Find as an alternative approach?", "3": "Is there a discussion on the appropriateness of the selected algorithm for the problem size?"}, "responses": {"Is Depth-First Search (DFS) or Breadth-First Search (BFS) being utilized, and why?": "10", "Has the candidate considered using Union-Find as an alternative approach?": "10", "Is there a discussion on the appropriateness of the selected algorithm for the problem size?": "7"}, "accumulated_result": 9.1}, "1": {"metrics": {"1": "Has the candidate defined what type of graph is being used (directed/undirected)?", "2": "Are the assumptions regarding input types and constraints clarified?", "3": "Is there a discussion about whether the graph is cyclic or acyclic?"}, "responses": {"Has the candidate defined what type of graph is being used (directed/undirected)?": "10", "Are the assumptions regarding input types and constraints clarified?": "5", "Is there a discussion about whether the graph is cyclic or acyclic?": "5"}, "accumulated_result": 7.0}, "2": {"metrics": {"1": "Does the candidate consider an empty graph as a valid input?", "2": "How does the solution handle graphs with a single node?", "3": "What happens if there are multiple cycles in the graph?"}, "responses": {"Does the candidate consider an empty graph as a valid input?": "10", "How does the solution handle graphs with a single node?": "1", "What happens if there are multiple cycles in the graph?": "1"}, "accumulated_result": 3.7}, "5": {"metrics": {"1": "What is the time complexity of the proposed solution?", "2": "Does the candidate mention how the complexity changes with different graph representations?", "3": "Is there a focus on improving the algorithms efficiency?"}, "responses": {"What is the time complexity of the proposed solution?": "10", "Does the candidate mention how the complexity changes with different graph representations?": "5", "Is there a focus on improving the algorithms efficiency?": "5"}, "accumulated_result": 7.0}, "6": {"metrics": {"1": "What is the space complexity of the proposed solution?", "2": "Does the candidate consider the memory overhead of the data structures used?", "3": "Is there any discussion on optimizing space usage?"}, "responses": {"What is the space complexity of the proposed solution?": "1", "Does the candidate consider the memory overhead of the data structures used?": "1", "Is there any discussion on optimizing space usage?": "1"}, "accumulated_result": 1.0}}, "accumulated_results_all_categories": {"3": 1.0, "7": 7.3, "4": 9.1, "1": 7.0, "2": 3.7, "5": 7.0, "6": 1.0}}'),
    (46, 3, 7, 5.29, '{"evaluation_results": {"2": {"criteria": {"1": "Does the candidate consider an empty graph as a valid input?", "2": "How does the solution handle graphs with a single node?", "3": "What happens if there are multiple cycles in the graph?"}, "responses": {"Does the candidate consider an empty graph as a valid input?": "10", "How does the solution handle graphs with a single node?": "1", "What happens if there are multiple cycles in the graph?": "1"}, "accumulated_result": 3.7}, "7": {"criteria": {"1": "Does the solution work for both small and large graphs?", "2": "Is there consideration for disconnected graphs?", "3": "How does the solution handle graphs with various node types or weights?"}, "responses": {"Does the solution work for both small and large graphs?": "10", "Is there consideration for disconnected graphs?": "10", "How does the solution handle graphs with various node types or weights?": "1"}, "accumulated_result": 7.3}, "6": {"criteria": {"1": "What is the space complexity of the proposed solution?", "2": "Does the candidate consider the memory overhead of the data structures used?", "3": "Is there any discussion on optimizing space usage?"}, "responses": {"What is the space complexity of the proposed solution?": "1", "Does the candidate consider the memory overhead of the data structures used?": "1", "Is there any discussion on optimizing space usage?": "1"}, "accumulated_result": 1.0}, "5": {"criteria": {"1": "What is the time complexity of the proposed solution?", "2": "Does the candidate mention how the complexity changes with different graph representations?", "3": "Is there a focus on improving the algorithms efficiency?"}, "responses": {"What is the time complexity of the proposed solution?": "10", "Does the candidate mention how the complexity changes with different graph representations?": "5", "Is there a focus on improving the algorithms efficiency?": "5"}, "accumulated_result": 7.0}, "3": {"criteria": {"1": "Is an adjacency list or matrix being used, and why?", "2": "Does the candidate discuss the trade-offs of using different data structures?", "3": "Is there consideration for the graphs density in choosing a data structure?"}, "responses": {"Is an adjacency list or matrix being used, and why?": "1", "Does the candidate discuss the trade-offs of using different data structures?": "1", "Is there consideration for the graphs density in choosing a data structure?": "1"}, "accumulated_result": 1.0}, "1": {"criteria": {"1": "Has the candidate defined what type of graph is being used (directed/undirected)?", "2": "Are the assumptions regarding input types and constraints clarified?", "3": "Is there a discussion about whether the graph is cyclic or acyclic?"}, "responses": {"Has the candidate defined what type of graph is being used (directed/undirected)?": "10", "Are the assumptions regarding input types and constraints clarified?": "7", "Is there a discussion about whether the graph is cyclic or acyclic?": "5"}, "accumulated_result": 7.6}, "4": {"criteria": {"1": "Is Depth-First Search (DFS) or Breadth-First Search (BFS) being utilized, and why?", "2": "Has the candidate considered using Union-Find as an alternative approach?", "3": "Is there a discussion on the appropriateness of the selected algorithm for the problem size?"}, "responses": {"Is Depth-First Search (DFS) or Breadth-First Search (BFS) being utilized, and why?": "10", "Has the candidate considered using Union-Find as an alternative approach?": "10", "Is there a discussion on the appropriateness of the selected algorithm for the problem size?": "8"}, "accumulated_result": 9.4}}, "accumulated_results_all_categories": {"2": 3.7, "7": 7.3, "6": 1.0, "5": 7.0, "3": 1.0, "1": 7.6, "4": 9.4}}');