from typing import cast

from graphql import (
    FragmentDefinitionNode,
    OperationDefinitionNode,
    build_ast_schema,
    parse,
)

from ariadne_codegen.generators.result_types import ResultTypesGenerator

from ...utils import format_graphql_str
from .schema import SCHEMA_STR


def test_get_operation_as_str_returns_str_with_added_typename():
    query_str = format_graphql_str(
        """
        query CustomQuery {
            query4 {
                ... on CustomType1 {
                    fielda
                }
                ... on CustomType2 {
                    fieldb
                }
            }
        }
        """
    )
    expected_result = format_graphql_str(
        """
        query CustomQuery {
            query4 {
                __typename
                ... on CustomType1 {
                    fielda
                }
                ... on CustomType2 {
                    fieldb
                }
            }
        }
        """
    )
    generator = ResultTypesGenerator(
        schema=build_ast_schema(parse(SCHEMA_STR)),
        operation_definition=cast(
            OperationDefinitionNode, parse(query_str).definitions[0]
        ),
        enums_module_name="enums",
    )

    result = generator.get_operation_as_str()

    assert result == expected_result


def test_get_operation_as_str_returns_str_with_used_fragments():
    query_str = format_graphql_str(
        """
        query CustomQuery {
            query2 {
                ...TestFragment1
                ...TestFragment2
                field2 {
                    fieldb
                }
            }
        }
        """
    )

    used_fragment1 = format_graphql_str(
        """
        fragment TestFragment1 on CustomType {
            id
        }
    """
    )

    used_fragment2 = format_graphql_str(
        """
        fragment TestFragment2 on CustomType {
            field1 {
                fielda
            }
        }
        """
    )

    not_used_fragment = format_graphql_str(
        """
        fragment TestFragment3 on CustomType {
            field2 {
                fieldb
            }
        }
        """
    )

    generator = ResultTypesGenerator(
        schema=build_ast_schema(parse(SCHEMA_STR)),
        operation_definition=cast(
            OperationDefinitionNode, parse(query_str).definitions[0]
        ),
        enums_module_name="enums",
        fragments_definitions={
            "TestFragment1": cast(
                FragmentDefinitionNode, parse(used_fragment1).definitions[0]
            ),
            "TestFragment2": cast(
                FragmentDefinitionNode, parse(used_fragment2).definitions[0]
            ),
            "TestFragment3": cast(
                FragmentDefinitionNode, parse(not_used_fragment).definitions[0]
            ),
        },
    )

    result = generator.get_operation_as_str()

    assert query_str in result
    assert used_fragment1 in result
    assert used_fragment2 in result
    assert not_used_fragment not in result
    assert result.index(used_fragment1) < result.index(used_fragment2)
